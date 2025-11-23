"""Modelos para el agente de detección de conflictos."""

from pydantic import BaseModel, Field


class Articulo(BaseModel):
    """Modelo para representar un artículo de un proyecto de ley."""

    numero: int
    tipo: str
    texto: str
    descripcion_semantica: str


class ProyectoLey(BaseModel):
    """Modelo para representar un proyecto de ley."""

    id: str
    titulo: str
    camara_origen: str
    tipo_proyecto: str
    etapa: int
    urgencia_actual: str
    fecha: str
    articulos: list[Articulo]


class ConflictoDetectado(BaseModel):
    """Modelo para representar un conflicto detectado entre una página y un artículo."""

    proyecto_id: str
    proyecto_titulo: str
    articulo_numero: int
    articulo_tipo: str
    pagina_numero: int
    similitud: float
    pagina_texto: str
    articulo_texto: str

    def __str__(self) -> str:
        """Retorna el conflicto como JSON string para usar con llm_map."""
        return f"## Documento Interno de la Empresa:\n\n{self.pagina_texto}\n\nArtículo de ley:\n\n{self.articulo_texto}"


class ImpactoConflictoLLM(BaseModel):
    """Modelo para el output del LLM al analizar un conflicto."""

    extracto_interno: str = Field(
        ...,
        description="Extracto específico del documento interno (memoria o archivo corporativo) que presenta conflicto o relación directa con el artículo propuesto. Debe incluir únicamente el texto pertinente que evidencia la discrepancia o impacto regulatorio.",
    )
    extracto_articulo: str = Field(
        ...,
        description="Extracto preciso del artículo de la propuesta de ley que genera el conflicto o impacto sobre las operaciones de la empresa. Debe contener exclusivamente la porción del texto legal relevante para la comparación.",
    )
    nivel_relevancia: int = Field(
        ...,
        description="Nivel de relevancia del impacto identificado en escala 0-100, donde 0 representa impacto nulo y 100 representa impacto crítico que requiere atención inmediata del equipo legal y alta dirección.",
        ge=0,
        le=100,
    )
    descripcion_impacto: str = Field(
        ...,
        description="Análisis técnico-legal del impacto regulatorio. Debe ser conciso, preciso y detallado, identificando: (1) naturaleza del conflicto o discrepancia, (2) implicaciones operativas y/o de cumplimiento, (3) riesgos legales potenciales. Redactado en lenguaje jurídico apropiado para el equipo legal corporativo.",
    )


class ImpactoConflicto(BaseModel):
    """Modelo completo para representar el impacto de un conflicto detectado."""

    articulo_numero: int
    extracto_interno: str
    extracto_articulo: str
    nivel_relevancia: int
    descripcion_impacto: str


class ProyectoLeyImpacto(BaseModel):
    """Modelo para representar el impacto de un proyecto de ley."""

    proyecto_id: str
    proyecto_titulo: str
    impactos: list[ImpactoConflicto]
    max_nivel_relevancia: int = 0
    descripcion_impacto_consolidada: str | None = None
