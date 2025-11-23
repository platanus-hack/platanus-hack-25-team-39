"""Nodos del grafo del agente de detección de conflictos."""

import hashlib
import logging

import numpy as np
from django.conf import settings
from openai import OpenAI

from .llm_map import llm_map
from .models import (
    ConflictoDetectado,
    ImpactoConflicto,
    ImpactoConflictoLLM,
    ProyectoLey,
    ProyectoLeyImpacto,
)
from .prompts import (
    MAP_CONSOLIDACION_BAJA_RELEVANCIA,
    MAP_CONSOLIDACION_DESCRIPCIONES,
    MAP_EXTRACCION_MATRICES,
)
from .state import ConflictDetectorState

logger = logging.getLogger(__name__)

# Variables globales de configuración
SIMILITUD_THRESHOLD = 0.325
MAX_ARTICULOS_POR_PAGINA = 10
EMBEDDING_MODEL = "text-embedding-3-small"

# Inicializar cliente de OpenAI
_client = None


def get_openai_client() -> OpenAI:
    """Obtiene o crea el cliente de OpenAI."""
    global _client
    _client = OpenAI(api_key=settings.PROJECT_OPENAI_API_KEY)
    return _client


def similitud_coseno(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calcula la similitud coseno entre dos vectores.

    Args:
        vec1: Primer vector
        vec2: Segundo vector

    Returns:
        Valor de similitud coseno (entre -1 y 1)
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def generar_embeddings(textos: list[str], batch_size: int = 100) -> list[list[float]]:
    """
    Genera embeddings usando la API de OpenAI con caché para evitar llamadas redundantes.

    Args:
        textos: Lista de textos a convertir en embeddings
        batch_size: Tamaño del lote para procesamiento

    Returns:
        Lista de vectores de embeddings
    """
    from apps.conflict_detector.models import EmbeddingCache

    # Filtrar y validar textos antes de procesar
    textos_validos = []
    indices_validos = []

    for idx, texto in enumerate(textos):
        # Validar que el texto sea string, no None, y no esté vacío
        if isinstance(texto, str) and texto.strip():
            textos_validos.append(texto)
            indices_validos.append(idx)
        else:
            # Para textos inválidos, usar un espacio como placeholder
            textos_validos.append(" ")
            indices_validos.append(idx)

    # Calcular hashes para todos los textos
    text_hashes = [
        hashlib.sha256(texto.encode("utf-8")).hexdigest() for texto in textos_validos
    ]

    # Buscar embeddings en caché
    logger.info(
        f"Buscando {len(text_hashes)} hashes en caché (modelo: {EMBEDDING_MODEL})"
    )
    cached_embeddings = EmbeddingCache.objects.filter(
        text_hash__in=text_hashes, model_name=EMBEDDING_MODEL
    ).in_bulk(field_name="text_hash")
    logger.info(f"Encontrados {len(cached_embeddings)} embeddings en caché")

    # Identificar textos que necesitan generar embeddings
    textos_to_generate = []
    indices_to_generate = []
    hash_to_index = {}

    cache_hits = 0
    cache_misses = 0
    for idx, (texto, text_hash) in enumerate(zip(textos_validos, text_hashes)):
        if text_hash in cached_embeddings:
            # Ya está en caché
            cache_hits += 1
            hash_to_index[text_hash] = idx
        else:
            # Necesita generar embedding
            cache_misses += 1
            textos_to_generate.append(texto)
            indices_to_generate.append(idx)
            hash_to_index[text_hash] = idx

    logger.info(f"Cache hits: {cache_hits}, Cache misses: {cache_misses}")

    # Generar embeddings para textos no cacheados
    nuevos_embeddings = {}
    if textos_to_generate:
        logger.info(
            f"Generando {len(textos_to_generate)} embeddings nuevos "
            f"({len(cached_embeddings)} encontrados en caché)"
        )

        client = get_openai_client()
        nuevos_embeddings_list = []

        # Procesar en lotes para manejar rate limits
        for i in range(0, len(textos_to_generate), batch_size):
            batch = textos_to_generate[i : i + batch_size]

            try:
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=batch,
                )

                batch_embeddings = [item.embedding for item in response.data]
                nuevos_embeddings_list.extend(batch_embeddings)

            except Exception as e:
                logger.error(f"Error al procesar lote {i // batch_size + 1}: {e}")
                raise

        # Guardar nuevos embeddings en caché
        embeddings_to_cache = []
        for idx, texto in enumerate(textos_to_generate):
            text_hash = hashlib.sha256(texto.encode("utf-8")).hexdigest()
            embedding = nuevos_embeddings_list[idx]

            embeddings_to_cache.append(
                EmbeddingCache(
                    text_hash=text_hash,
                    embedding=embedding,
                    model_name=EMBEDDING_MODEL,
                    dimension=len(embedding),
                )
            )
            nuevos_embeddings[text_hash] = embedding

        # Bulk insert de nuevos embeddings
        if embeddings_to_cache:
            EmbeddingCache.objects.bulk_create(
                embeddings_to_cache, ignore_conflicts=True
            )
            logger.info(f"Guardados {len(embeddings_to_cache)} embeddings en caché")
    else:
        logger.info(
            f"Todos los embeddings ({len(cached_embeddings)}) encontrados en caché"
        )

    # Reconstruir lista de embeddings en el orden original
    embeddings = []
    for text_hash in text_hashes:
        if text_hash in cached_embeddings:
            # Obtener de caché
            embeddings.append(list(cached_embeddings[text_hash].embedding))
        else:
            # Obtener de nuevos embeddings
            embeddings.append(nuevos_embeddings[text_hash])

    return embeddings


def load_proyectos_ley() -> list[ProyectoLey]:
    """
    Carga los proyectos de ley desde la base de datos.

    Returns:
        Lista de proyectos de ley cargados como modelos Pydantic
    """
    from apps.proyectos_ley.models import ProyectoLey as ProyectoLeyDB

    from .models import Articulo as ArticuloPydantic

    proyectos = []

    # Obtener todos los proyectos de ley con sus artículos
    proyectos_db = ProyectoLeyDB.objects.prefetch_related("articulos").all()

    for proyecto_db in proyectos_db:
        # Convertir artículos de Django a Pydantic
        articulos_pydantic = [
            ArticuloPydantic(
                numero=articulo.numero,
                tipo=articulo.tipo,
                texto=articulo.texto,
                descripcion_semantica=articulo.descripcion_semantica,
            )
            for articulo in proyecto_db.articulos.all()
        ]

        # Crear el modelo Pydantic del proyecto
        proyecto = ProyectoLey(
            id=proyecto_db.proyecto_id,
            titulo=proyecto_db.titulo,
            camara_origen=proyecto_db.camara_origen,
            tipo_proyecto=proyecto_db.tipo_proyecto,
            etapa=proyecto_db.etapa,
            urgencia_actual=proyecto_db.urgencia_actual,
            fecha=proyecto_db.fecha.isoformat(),
            articulos=articulos_pydantic,
        )
        proyectos.append(proyecto)

    logger.info(f"Cargados {len(proyectos)} proyectos de ley desde la base de datos")
    return proyectos


def detectar_conflictos(
    document_pages: list[str],
    articulos_con_proyecto: list[dict],
) -> list[ConflictoDetectado]:
    """
    Detecta conflictos comparando cada página con cada artículo.

    Args:
        document_pages: Lista de páginas del documento
        proyectos_ley: Lista de proyectos de ley

    Returns:
        Lista de conflictos detectados
    """

    if not articulos_con_proyecto or not document_pages:
        return []

    # Filtrar páginas vacías antes de generar embeddings
    paginas_validas = []
    indices_paginas_validas = []
    for idx, pagina in enumerate(document_pages):
        if isinstance(pagina, str) and pagina.strip():
            paginas_validas.append(pagina)
            indices_paginas_validas.append(idx)

    if not paginas_validas:
        logger.warning("No hay páginas válidas para procesar")
        return []

    # Generar embeddings para páginas válidas
    logger.info(
        f"Generando embeddings para {len(paginas_validas)} páginas válidas (de {len(document_pages)} totales)"
    )
    embeddings_paginas = generar_embeddings(paginas_validas)
    embeddings_paginas_np = np.array(embeddings_paginas)

    # Generar embeddings para artículos (filtrar artículos con descripcion_semantica vacía)
    articulos_validos = []
    textos_articulos = []
    for item in articulos_con_proyecto:
        desc_sem = item["articulo"].descripcion_semantica
        # Filtrar artículos con descripcion_semantica vacía o inválida
        textos_articulos.append(desc_sem)
        articulos_validos.append(item)

    if not textos_articulos:
        logger.warning("No hay artículos válidos para procesar")
        return []

    logger.info(f"Generando embeddings para {len(textos_articulos)} artículos")
    embeddings_articulos = generar_embeddings(textos_articulos)
    embeddings_articulos_np = np.array(embeddings_articulos)
    # Comparar cada página válida con cada artículo
    conflictos = []

    for idx, pagina_num_original in enumerate(indices_paginas_validas):
        pagina_text = paginas_validas[idx]
        embedding_pagina = embeddings_paginas_np[idx]

        # Calcular similitud con todos los artículos válidos
        similitudes_articulos = []
        for art_idx, item in enumerate(articulos_validos):
            embedding_articulo = embeddings_articulos_np[art_idx]
            similitud = similitud_coseno(embedding_pagina, embedding_articulo)
            if similitud >= SIMILITUD_THRESHOLD:
                similitudes_articulos.append(
                    {
                        "proyecto_id": item["proyecto_id"],
                        "proyecto_titulo": item["proyecto_titulo"],
                        "articulo": item["articulo"],
                        "similitud": similitud,
                    }
                )

        # Ordenar por similitud descendente
        similitudes_articulos.sort(key=lambda x: x["similitud"], reverse=True)

        # Crear conflictos detectados
        for item in similitudes_articulos:
            conflicto = ConflictoDetectado(
                proyecto_id=item["proyecto_id"],
                proyecto_titulo=item["proyecto_titulo"],
                articulo_numero=item["articulo"].numero,
                articulo_tipo=item["articulo"].tipo,
                pagina_numero=pagina_num_original,  # Usar el número de página original
                similitud=item["similitud"],
                pagina_texto=pagina_text,
                articulo_texto=item["articulo"].texto,
            )
            conflictos.append(conflicto)

    logger.info(f"Detectados {len(conflictos)} conflictos potenciales")
    return conflictos


def _format_descriptions_for_consolidation(descriptions: list[str]) -> str:
    """
    Formatea una lista de descripciones para consolidación.

    Args:
        descriptions: Lista de descripciones de impacto

    Returns:
        String formateado con descripciones numeradas
    """
    return "\n\n".join(
        f"## Impacto {i + 1}\n{desc}" for i, desc in enumerate(descriptions)
    )


def consolidate_descriptions_batch(
    descriptions_list: list[list[str]],
) -> list[str]:
    """
    Consolida múltiples listas de descripciones en paralelo usando llm_map.

    Args:
        descriptions_list: Lista de listas de descripciones a consolidar

    Returns:
        Lista de descripciones consolidadas
    """
    if not descriptions_list:
        return []

    # Preparar textos para procesar
    texts_to_process: list[str] = []
    indices_to_process: list[int] = []
    results: list[str] = [""] * len(descriptions_list)

    for idx, descriptions in enumerate(descriptions_list):
        if not descriptions:
            results[idx] = ""
        elif len(descriptions) == 1:
            results[idx] = descriptions[0]
        else:
            formatted = _format_descriptions_for_consolidation(descriptions)
            texts_to_process.append(formatted)
            indices_to_process.append(idx)

    if not texts_to_process:
        return results

    # Usar llm_map para procesar en paralelo
    logger.info(
        f"Consolidando {len(texts_to_process)} grupos de descripciones en paralelo"
    )
    result = llm_map(
        texts=texts_to_process,
        map_prompt=MAP_CONSOLIDACION_DESCRIPCIONES,
        map_output_parser=None,  # String output
        llm_temperature=0.3,
        concurrency_limit=32,
    )

    # Mapear resultados
    for i, idx in enumerate(indices_to_process):
        results[idx] = str(result.map_results[i])

    logger.info(f"Consolidación completada para {len(texts_to_process)} grupos")
    return results


def consolidate_low_relevance_batch(
    descriptions_list: list[list[str]],
) -> list[str]:
    """
    Genera resúmenes de baja relevancia para múltiples listas en paralelo.

    Args:
        descriptions_list: Lista de listas de descripciones de baja relevancia

    Returns:
        Lista de resúmenes explicando por qué no son significativos
    """
    if not descriptions_list:
        return []

    # Preparar textos para procesar
    texts_to_process: list[str] = []
    indices_to_process: list[int] = []
    results: list[str] = [""] * len(descriptions_list)

    for idx, descriptions in enumerate(descriptions_list):
        if not descriptions:
            results[idx] = ""
        else:
            formatted = _format_descriptions_for_consolidation(descriptions)
            texts_to_process.append(formatted)
            indices_to_process.append(idx)

    if not texts_to_process:
        return results

    # Usar llm_map para procesar en paralelo
    logger.info(
        f"Generando {len(texts_to_process)} resúmenes de baja relevancia en paralelo"
    )
    result = llm_map(
        texts=texts_to_process,
        map_prompt=MAP_CONSOLIDACION_BAJA_RELEVANCIA,
        map_output_parser=None,  # String output
        llm_temperature=0.3,
        concurrency_limit=32,
    )

    # Mapear resultados
    for i, idx in enumerate(indices_to_process):
        results[idx] = str(result.map_results[i])

    logger.info(
        f"Resúmenes de baja relevancia completados para {len(texts_to_process)} grupos"
    )
    return results


def calcular_impacto_conflictos(conflictos: list[ConflictoDetectado]):
    """
    Calcula el impacto de los conflictos detectados usando LLM con llm_map.

    Args:
        conflictos: Lista de conflictos detectados

    Returns:
        MapResult con los resultados del procesamiento LLM
    """
    if not conflictos:
        from .llm_map import MapResult

        return MapResult(map_results=[])

    # Convertir conflictos a strings usando __str__
    textos_para_procesar = [str(conflicto) for conflicto in conflictos]

    # Usar llm_map para procesar los conflictos (usa ImpactoConflictoLLM para el LLM)
    result = llm_map(
        texts=textos_para_procesar,
        map_prompt=MAP_EXTRACCION_MATRICES,
        map_output_parser=ImpactoConflictoLLM,
        concurrency_limit=128,
    )

    logger.info(f"Impacto calculado para {len(result.map_results)} conflictos")

    return result


def process_document(state: ConflictDetectorState) -> ConflictDetectorState:
    """
    Procesa las páginas del documento y carga los proyectos de ley.

    Detecta conflictos comparando cada página con cada artículo.
    """
    document_pages = state.document_pages
    logger.info(f"Procesando documento con {len(document_pages)} páginas")

    # Cargar proyectos de ley
    proyectos_ley = load_proyectos_ley()

    # Extraer artículos distintos
    articulos_con_proyecto = []
    for proyecto in proyectos_ley:
        for articulo in proyecto.articulos:
            articulos_con_proyecto.append(
                {
                    "proyecto_id": proyecto.id,
                    "proyecto_titulo": proyecto.titulo,
                    "articulo": articulo,
                }
            )

    logger.info(f"Total de artículos a comparar: {len(articulos_con_proyecto)}")

    # Detectar conflictos
    conflictos = detectar_conflictos(document_pages, articulos_con_proyecto)

    # Calcular impacto de los conflictos usando LLM
    conflictos_impacto = calcular_impacto_conflictos(conflictos)

    # Combinar conflictos originales con impactos calculados y agrupar por proyecto
    proyectos_ley_impacto = []

    if conflictos and conflictos_impacto.map_results:
        # Crear un diccionario para agrupar impactos por proyecto
        proyectos_impacto = {}

        # Combinar cada conflicto con su impacto correspondiente
        impactos_sin_relacion_count = 0

        for conflicto, impacto_llm in zip(conflictos, conflictos_impacto.map_results):
            # Filtrar solo impactos donde el modelo indicó explícitamente sin relación
            if impacto_llm.nivel_relevancia == 0:
                logger.info(
                    f"Impacto descartado (sin relación) - Proyecto: {conflicto.proyecto_id}, "
                    f"Artículo: {conflicto.articulo_numero}"
                )
                impactos_sin_relacion_count += 1
                continue

            proyecto_id = conflicto.proyecto_id
            proyecto_titulo = conflicto.proyecto_titulo

            if proyecto_id not in proyectos_impacto:
                proyectos_impacto[proyecto_id] = {
                    "proyecto_id": proyecto_id,
                    "proyecto_titulo": proyecto_titulo,
                    "impactos": [],
                }

            # Crear ImpactoConflicto con articulo_numero del conflicto
            impacto = ImpactoConflicto(
                articulo_numero=conflicto.articulo_numero,
                extracto_interno=impacto_llm.extracto_interno,
                extracto_articulo=impacto_llm.extracto_articulo,
                nivel_relevancia=impacto_llm.nivel_relevancia,
                descripcion_impacto=impacto_llm.descripcion_impacto,
            )
            proyectos_impacto[proyecto_id]["impactos"].append(impacto)

        if impactos_sin_relacion_count > 0:
            logger.info(
                f"Total de impactos descartados por baja relevancia: {impactos_sin_relacion_count}"
            )

        # Construir lista de ProyectoLeyImpacto con consolidación paralela
        proyectos_ley_impacto = []
        if proyectos_impacto:
            # Fase 1: Recopilar descripciones por proyecto
            proyecto_ids = list(proyectos_impacto.keys())
            high_relevance_by_project: list[list[str]] = []
            low_relevance_by_project: list[list[str]] = []
            max_relevancia_by_project: list[int] = []
            use_high_relevance: list[bool] = []

            for proyecto_id in proyecto_ids:
                proyecto = proyectos_impacto[proyecto_id]
                high_relevance_descriptions = []
                low_relevance_descriptions = []
                max_nivel_relevancia = 0

                for impacto in proyecto["impactos"]:
                    if impacto.nivel_relevancia > max_nivel_relevancia:
                        max_nivel_relevancia = impacto.nivel_relevancia

                    if impacto.nivel_relevancia > 50:
                        high_relevance_descriptions.append(impacto.descripcion_impacto)
                    else:
                        low_relevance_descriptions.append(impacto.descripcion_impacto)

                high_relevance_by_project.append(high_relevance_descriptions)
                low_relevance_by_project.append(low_relevance_descriptions)
                max_relevancia_by_project.append(max_nivel_relevancia)
                use_high_relevance.append(len(high_relevance_descriptions) > 0)

            # Fase 2: Consolidar en paralelo (separar high y low relevance)
            high_to_consolidate = [
                descs
                for descs, use_high in zip(
                    high_relevance_by_project, use_high_relevance
                )
                if use_high
            ]
            low_to_consolidate = [
                descs
                for descs, use_high in zip(low_relevance_by_project, use_high_relevance)
                if not use_high
            ]

            # Ejecutar consolidaciones en paralelo
            high_results = consolidate_descriptions_batch(high_to_consolidate)
            low_results = consolidate_low_relevance_batch(low_to_consolidate)

            # Fase 3: Reconstruir resultados en orden original
            high_idx = 0
            low_idx = 0
            consolidated_descriptions: list[str] = []

            for use_high in use_high_relevance:
                if use_high:
                    consolidated_descriptions.append(high_results[high_idx])
                    high_idx += 1
                else:
                    consolidated_descriptions.append(low_results[low_idx])
                    low_idx += 1

            # Fase 4: Crear objetos ProyectoLeyImpacto
            for i, proyecto_id in enumerate(proyecto_ids):
                proyecto = proyectos_impacto[proyecto_id]
                proyecto_ley_impacto_obj = ProyectoLeyImpacto(
                    proyecto_id=proyecto["proyecto_id"],
                    proyecto_titulo=proyecto["proyecto_titulo"],
                    impactos=proyecto["impactos"],
                    max_nivel_relevancia=max_relevancia_by_project[i],
                    descripcion_impacto_consolidada=consolidated_descriptions[i],
                )
                proyectos_ley_impacto.append(proyecto_ley_impacto_obj)
                logger.info(
                    f"Proyecto {proyecto_id}: {len(proyecto['impactos'])} impactos totales, "
                    f"{len(high_relevance_by_project[i])} relevantes (>50), "
                    f"{len(low_relevance_by_project[i])} baja relevancia, "
                    f"max_relevancia={max_relevancia_by_project[i]}"
                )

    logger.info(
        f"Procesamiento completado: {len(proyectos_ley_impacto)} proyectos con impacto"
    )
    state.proyecto_ley_impacto = proyectos_ley_impacto
    return state
