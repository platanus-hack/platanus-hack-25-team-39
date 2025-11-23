"""Servicios para el conflict detector."""

import fitz  # PyMuPDF
from asgiref.sync import sync_to_async

from .agent.graph import run_agent
from .agent.models import ProyectoLeyImpacto
from .models import Documento, DescubrimientoConflicto, ImpactoDescubierto


def extract_text_from_pdf(pdf_content: bytes) -> list[str]:
    """
    Extrae el texto de cada página de un PDF.

    Args:
        pdf_content: Contenido del PDF en bytes

    Returns:
        Lista con el texto de cada página
    """
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    pages_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages_text.append(text)
    doc.close()
    return pages_text


def crear_documento(nombre: str, user) -> Documento:
    """
    Crea un documento en la base de datos.

    Args:
        nombre: Nombre del documento
        user: Usuario que sube el documento

    Returns:
        El objeto Documento creado
    """
    return Documento.objects.create(nombre=nombre, user=user)


def guardar_descubrimientos(
    documento: Documento,
    impactos: list[ProyectoLeyImpacto],
) -> dict:
    """
    Guarda los descubrimientos de conflictos en la base de datos.

    Args:
        documento: Documento analizado
        impactos: Lista de ProyectoLeyImpacto detectados

    Returns:
        Diccionario con documento y descubrimientos serializados
    """
    descubrimientos_data = []

    for proyecto_impacto in impactos:
        # Crear el descubrimiento (uno por proyecto)
        descubrimiento = DescubrimientoConflicto.objects.create(
            documento=documento,
            proyecto_id=proyecto_impacto.proyecto_id,
            proyecto_titulo=proyecto_impacto.proyecto_titulo,
            max_nivel_relevancia=proyecto_impacto.max_nivel_relevancia,
            descripcion_impacto_consolidada=proyecto_impacto.descripcion_impacto_consolidada,
        )

        # Crear los impactos individuales
        cantidad_impactos = 0
        for impacto in proyecto_impacto.impactos:
            ImpactoDescubierto.objects.create(
                descubrimiento=descubrimiento,
                articulo_numero=impacto.articulo_numero,
                extracto_interno=impacto.extracto_interno,
                extracto_articulo=impacto.extracto_articulo,
                nivel_relevancia=impacto.nivel_relevancia,
                descripcion_impacto=impacto.descripcion_impacto,
            )
            cantidad_impactos += 1

        descubrimientos_data.append({
            "id": descubrimiento.id,
            "proyecto_id": descubrimiento.proyecto_id,
            "proyecto_titulo": descubrimiento.proyecto_titulo,
            "max_nivel_relevancia": descubrimiento.max_nivel_relevancia,
            "descripcion_impacto_consolidada": descubrimiento.descripcion_impacto_consolidada,
            "cantidad_impactos": cantidad_impactos,
        })

    return {
        "documento_id": documento.id,
        "documento_nombre": documento.nombre,
        "fecha_carga": documento.fecha_carga.isoformat(),
        "descubrimientos": descubrimientos_data,
    }


async def detect_conflicts(pdf_content: bytes, nombre_documento: str = "", user=None) -> dict:
    """
    Detecta conflictos usando el agente LangGraph y guarda el descubrimiento.

    Args:
        pdf_content: Contenido del archivo PDF en bytes
        nombre_documento: Nombre opcional del documento analizado
        user: Usuario que sube el documento

    Returns:
        Diccionario con el documento, los descubrimientos y el conteo de pendientes
    """
    # Crear el documento primero
    documento = await sync_to_async(crear_documento)(nombre_documento, user)

    # Extraer texto de cada página del PDF
    document_pages = await sync_to_async(extract_text_from_pdf)(pdf_content)

    # Ejecutar el agente de forma asíncrona usando sync_to_async
    impactos = await sync_to_async(run_agent)(document_pages)

    # Guardar los descubrimientos en la base de datos
    result = await sync_to_async(guardar_descubrimientos)(documento, impactos)

    # Contar descubrimientos pendientes del usuario
    pending_count = await sync_to_async(
        lambda: DescubrimientoConflicto.objects.filter(
            documento__user=user,
            estado=DescubrimientoConflicto.Estado.PENDING
        ).count()
    )()

    # Agregar el conteo al resultado
    result["pending_discoveries_count"] = pending_count

    return result
