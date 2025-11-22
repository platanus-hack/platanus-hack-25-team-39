"""Servicios para el conflict detector."""

import fitz  # PyMuPDF
from asgiref.sync import sync_to_async

from .agent.graph import run_agent


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


async def detect_conflicts(pdf_content: bytes) -> dict:
    """
    Detecta conflictos usando el agente LangGraph.

    Args:
        pdf_content: Contenido del archivo PDF en bytes

    Returns:
        Diccionario con resultado y conflictos detectados
    """
    # Extraer texto de cada página del PDF
    document_pages = await sync_to_async(extract_text_from_pdf)(pdf_content)

    # Ejecutar el agente de forma asíncrona usando sync_to_async
    result = await sync_to_async(run_agent)(document_pages)
    return result
