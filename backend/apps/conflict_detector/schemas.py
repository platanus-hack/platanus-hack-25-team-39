"""Schemas para el API de conflict detector."""

from datetime import datetime

from ninja import Schema


class ImpactoDescubiertoSchema(Schema):
    """Schema para un impacto descubierto."""

    id: int
    articulo_numero: int
    extracto_interno: str
    extracto_articulo: str
    nivel_relevancia: int
    descripcion_impacto: str
    created_at: datetime


class DescubrimientoConflictoSchema(Schema):
    """Schema para un descubrimiento de conflicto."""

    id: int
    proyecto_id: str
    proyecto_titulo: str
    descripcion_impacto_consolidada: str | None
    fecha_analisis: datetime
    impactos: list[ImpactoDescubiertoSchema]


class DocumentoListSchema(Schema):
    """Schema para listar documentos."""

    id: int
    nombre: str
    fecha_carga: datetime
    cantidad_descubrimientos: int


class DocumentoDetailSchema(Schema):
    """Schema para detalles de un documento."""

    id: int
    nombre: str
    fecha_carga: datetime
    descubrimientos: list[DescubrimientoConflictoSchema]


class DescubrimientoListSchema(Schema):
    """Schema para listar descubrimientos."""

    id: int
    proyecto_id: str
    proyecto_titulo: str
    descripcion_impacto_consolidada: str | None
    fecha_analisis: datetime
    cantidad_impactos: int
    max_nivel_relevancia: int
    documento_nombre: str
    documento_id: int
    estado: str
    proyecto_etapa: int | None = None
    proyecto_fecha: str | None = None
    proyecto_camara_origen: str | None = None


class DescubrimientoDetailSchema(Schema):
    """Schema para detalles de un descubrimiento específico."""

    id: int
    proyecto_id: str
    proyecto_titulo: str
    descripcion_impacto_consolidada: str | None
    fecha_analisis: datetime
    estado: str
    max_nivel_relevancia: int
    documento: DocumentoListSchema
    impactos: list[ImpactoDescubiertoSchema]
