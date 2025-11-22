"""Nodos del grafo del agente de detección de conflictos."""

import json
import os
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

from .models import ConflictoDetectado, ImpactoConflicto, ProyectoLey, ProyectoLeyImpacto
from .prompts import MAP_EXTRACCION_MATRICES, CONSOLIDACION_DESCRIPCIONES
from .state import ConflictDetectorState
from django.conf import settings
from .llm_map import llm_map


# Variables globales de configuración
SIMILITUD_THRESHOLD = 0.4
MAX_ARTICULOS_POR_PAGINA = 10
EMBEDDING_MODEL = "text-embedding-3-small"

# Inicializar cliente de OpenAI
_client = None


def get_openai_client() -> OpenAI:
    """Obtiene o crea el cliente de OpenAI."""
    print("settings.PROJECT_OPENAI_API_KEY: ", settings.PROJECT_OPENAI_API_KEY)
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
    Genera embeddings usando la API de OpenAI.

    Args:
        textos: Lista de textos a convertir en embeddings
        batch_size: Tamaño del lote para procesamiento

    Returns:
        Lista de vectores de embeddings
    """
    client = get_openai_client()
    embeddings = []

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

    # Procesar en lotes para manejar rate limits
    for i in range(0, len(textos_validos), batch_size):
        batch = textos_validos[i : i + batch_size]

        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch,
            )

            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)

            # Pequeña pausa para evitar rate limits
            time.sleep(0.1)

        except Exception as e:
            print(f"Error al procesar lote {i//batch_size + 1}: {e}")
            raise

    return embeddings


def load_proyectos_ley() -> list[ProyectoLey]:
    """
    Carga los proyectos de ley desde los archivos JSON en data/proyectos_ley/.

    Returns:
        Lista de proyectos de ley cargados
    """
    proyectos = []
    # Buscar el directorio data/proyectos_ley desde la raíz del backend
    # El path se construye desde el paquete hacia arriba hasta encontrar el backend
    backend_root = Path(__file__).parent.parent.parent.parent

    proyectos_dir = backend_root / "data" / "proyectos_ley"
    print("proyectos_dir: ", proyectos_dir)

    if not proyectos_dir.exists():
        return proyectos

    for json_file in proyectos_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                proyecto = ProyectoLey(**data)
                proyectos.append(proyecto)
        except Exception as e:
            # Si hay un error al cargar un archivo, lo ignoramos y continuamos
            print(f"Error al cargar {json_file}: {e}")
            continue

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
        print("No hay páginas válidas para procesar")
        return []

    # Generar embeddings para páginas válidas
    print(f"Generando embeddings para {len(paginas_validas)} páginas válidas (de {len(document_pages)} totales)...")
    embeddings_paginas = generar_embeddings(paginas_validas)
    embeddings_paginas_np = np.array(embeddings_paginas)
    print("embeddings_paginas_np: ", embeddings_paginas_np)

    # Generar embeddings para artículos (filtrar artículos con descripcion_semantica vacía)
    articulos_validos = []
    textos_articulos = []
    for item in articulos_con_proyecto:
        desc_sem = item["articulo"].descripcion_semantica
        # Filtrar artículos con descripcion_semantica vacía o inválida
        textos_articulos.append(desc_sem)
        articulos_validos.append(item)
    
    if not textos_articulos:
        print("No hay artículos válidos para procesar")
        return []
    
    print(f"Generando embeddings para {len(textos_articulos)} artículos...")
    embeddings_articulos = generar_embeddings(textos_articulos)
    embeddings_articulos_np = np.array(embeddings_articulos)
    print("embeddings_articulos_np: ", embeddings_articulos_np)
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
            else:
                print({
                        "proyecto_id": item["proyecto_id"],
                        "proyecto_titulo": item["proyecto_titulo"],
                        "articulo": item["articulo"],
                        "similitud": similitud,
                    })

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

    print("conflictos: ", conflictos)
    return conflictos


def consolidate_descriptions(descriptions: list[str]) -> str:
    """
    Consolida múltiples descripciones de impacto en un análisis único y coherente.

    Args:
        descriptions: Lista de descripciones de impacto a consolidar

    Returns:
        Descripción consolidada como string
    """
    if not descriptions:
        return ""
    
    if len(descriptions) == 1:
        return descriptions[0]
    
    # Formatear descripciones numeradas para el prompt
    formatted_descriptions = "\n\n".join(
        f"## Impacto {i+1}\n{desc}" 
        for i, desc in enumerate(descriptions)
    )
    
    # Preparar el prompt con las descripciones
    prompt_content = CONSOLIDACION_DESCRIPCIONES.format(
        descriptions=formatted_descriptions
    )
    
    # Llamar al LLM para consolidar
    client = get_openai_client()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un abogado senior especializado en análisis regulatorio corporativo."
                },
                {
                    "role": "user",
                    "content": prompt_content
                }
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        
        consolidated = response.choices[0].message.content.strip()
        print(f"✅ Consolidadas {len(descriptions)} descripciones de impacto")
        return consolidated
        
    except Exception as e:
        print(f"❌ Error al consolidar descripciones: {e}")
        # Fallback: concatenar descripciones con separadores
        return "\n\n---\n\n".join(
            f"**Impacto {i+1}**\n\n{desc}" 
            for i, desc in enumerate(descriptions)
        )


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

    # Usar llm_map para procesar los conflictos
    result = llm_map(
        texts=textos_para_procesar,
        map_prompt=MAP_EXTRACCION_MATRICES,
        map_output_parser=ImpactoConflicto,
        concurrency_limit=16,
    )

    print(f"✅ Impacto calculado para {len(result.map_results)} conflictos")

    return result

def process_document(state: ConflictDetectorState) -> ConflictDetectorState:
    """
    Procesa las páginas del documento y carga los proyectos de ley.

    Detecta conflictos comparando cada página con cada artículo.
    """
    document_pages = state.document_pages
    print("document_pages: ", document_pages)

    # Cargar proyectos de ley
    proyectos_ley = load_proyectos_ley()
    print("proyectos_ley: ", proyectos_ley)
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
    print("articulos_con_proyecto: ", articulos_con_proyecto)
    # Detectar conflictos
    conflictos = detectar_conflictos(document_pages, articulos_con_proyecto)
    
    # Calcular impacto de los conflictos usando LLM
    print("conflictos: ", conflictos)
    conflictos_impacto = calcular_impacto_conflictos(conflictos)
    print("conflictos_impacto: ", conflictos_impacto)

    # Combinar conflictos originales con impactos calculados y agrupar por proyecto
    proyecto_ley_impacto = None
    print("conflictos: ", conflictos)
    print("conflictos_impacto.map_results: ", conflictos_impacto.map_results)
    
    if conflictos and conflictos_impacto.map_results:
        # Crear un diccionario para agrupar impactos por proyecto
        proyectos_impacto = {}
        
        # Combinar cada conflicto con su impacto correspondiente
        for conflicto, impacto in zip(conflictos, conflictos_impacto.map_results):
            print("conflicto.proyecto_id: ", conflicto.proyecto_id)
            print("conflicto.proyecto_titulo: ", conflicto.proyecto_titulo)
            print("impacto: ", impacto)
            proyecto_id = conflicto.proyecto_id
            proyecto_titulo = conflicto.proyecto_titulo
            
            if proyecto_id not in proyectos_impacto:
                proyectos_impacto[proyecto_id] = {
                    "proyecto_id": proyecto_id,
                    "proyecto_titulo": proyecto_titulo,
                    "impactos": []
                }
            
            proyectos_impacto[proyecto_id]["impactos"].append(impacto)
        
        # Si hay al menos un proyecto, usar el primero (o podríamos retornar una lista)
        print("proyectos_impacto: ", proyectos_impacto)
        all_descriptions = []
        if proyectos_impacto:
            primer_proyecto = next(iter(proyectos_impacto.values()))
            proyecto_ley_impacto = ProyectoLeyImpacto(
                proyecto_id=primer_proyecto["proyecto_id"],
                proyecto_titulo=primer_proyecto["proyecto_titulo"],
                impactos=primer_proyecto["impactos"],
            )
            for impacto in primer_proyecto["impactos"]:
                if impacto.nivel_relevancia > 50:
                    all_descriptions.append(impacto.descripcion_impacto)
                else:
                    print("impacto.nivel_relevancia: ", impacto.nivel_relevancia)
        print("all_descriptions: ", all_descriptions)
        description = consolidate_descriptions(all_descriptions)


    # Actualizar el estado
    #state.proyectos_ley = proyectos_ley
    ##state.conflictos = conflictos
    state.proyecto_ley_impacto = proyecto_ley_impacto
    state.descripcion_impacto_consolidada = description

    print("state: ", state)
    return state
