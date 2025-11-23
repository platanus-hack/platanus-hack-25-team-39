"""Estado del agente de detección de conflictos."""

from pydantic import BaseModel

from .models import ConflictoDetectado, ProyectoLey, ProyectoLeyImpacto


class ConflictDetectorState(BaseModel):
    """Estado del agente de detección de conflictos."""

    document_pages: list[str]
    proyectos_ley: list[ProyectoLey] = []
    articulos_con_proyecto: list[dict] = []
    conflictos: list[ConflictoDetectado] = []
    proyecto_ley_impacto: list[ProyectoLeyImpacto] = []
