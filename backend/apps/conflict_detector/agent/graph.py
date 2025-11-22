"""Grafo del agente de detección de conflictos."""

from langgraph.graph import StateGraph

from .models import ConflictoDetectado
from .nodes import process_document
from .state import ConflictDetectorState


def create_agent() -> StateGraph:
    """Crea y retorna el grafo del agente."""
    workflow = StateGraph(ConflictDetectorState)

    # Agregar nodo de procesamiento
    workflow.add_node("process", process_document)

    # Definir el punto de entrada
    workflow.set_entry_point("process")

    # Compilar el grafo
    return workflow.compile()


def format_conflictos_output(conflictos: list[ConflictoDetectado]) -> dict:
    """
    Formatea los conflictos detectados por proyecto y artículo.

    Args:
        conflictos: Lista de conflictos detectados

    Returns:
        Diccionario estructurado: {proyecto_id: {articulo_numero: [paginas]}}
    """
    resultado = {}

    for conflicto in conflictos:
        proyecto_id = conflicto.proyecto_id
        articulo_num = conflicto.articulo_numero
        pagina_num = conflicto.pagina_numero

        if proyecto_id not in resultado:
            resultado[proyecto_id] = {}

        if articulo_num not in resultado[proyecto_id]:
            resultado[proyecto_id][articulo_num] = []

        if pagina_num not in resultado[proyecto_id][articulo_num]:
            resultado[proyecto_id][articulo_num].append(pagina_num)

    # Ordenar páginas en cada artículo
    for proyecto_id in resultado:
        for articulo_num in resultado[proyecto_id]:
            resultado[proyecto_id][articulo_num].sort()

    return resultado


def run_agent(document_pages: list[str]) -> dict:
    """
    Ejecuta el agente con las páginas del documento.

    Args:
        document_pages: Lista con el texto de cada página del documento

    Returns:
        Diccionario con resultado y conflictos formateados
    """
    agent = create_agent()
    initial_state = ConflictDetectorState(document_pages=document_pages)
    result = agent.invoke(initial_state)
    print("result: ", result)

    return result

