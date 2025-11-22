"""API endpoints para conflict detector."""

from ninja import File, Router, UploadedFile

from .services import detect_conflicts


router = Router()


@router.post("/detect", auth=None)
async def detect_conflicts_endpoint(request, file: UploadedFile = File(...)):
    """
    Detecta conflictos usando el agente LangGraph.

    Recibe un archivo PDF y retorna el resultado del análisis del agente.
    Los conflictos están organizados por proyecto y artículo, indicando las páginas con conflicto.
    """
    # Leer el contenido del archivo PDF (read() es síncrono, no necesita await)
    pdf_content = file.read()

    # Procesar el PDF y detectar conflictos
    result = await detect_conflicts(pdf_content)
    return result
