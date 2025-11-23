"""
Proyectos de Ley API

This module implements the HTTP endpoints for accessing proyectos de ley.
"""

from ninja import Query, Router, Schema

from .models import Articulo, ProyectoLey


class ArticuloOut(Schema):
    """Output schema for articulos."""

    id: int
    numero: int
    tipo: str
    texto: str
    descripcion_semantica: str


class ProyectoLeyOut(Schema):
    """Output schema for proyectos de ley (list view)."""

    id: int
    proyecto_id: str
    titulo: str
    camara_origen: str
    tipo_proyecto: str
    etapa: int
    urgencia_actual: str
    fecha: str
    articulos_count: int


class ProyectoLeyDetailOut(Schema):
    """Output schema for proyecto de ley detail with articulos."""

    id: int
    proyecto_id: str
    titulo: str
    camara_origen: str
    tipo_proyecto: str
    etapa: int
    urgencia_actual: str
    fecha: str
    articulos: list[ArticuloOut]


class ProyectosLeyResponse(Schema):
    """Response schema for proyectos de ley list endpoint."""

    proyectos: list[ProyectoLeyOut]
    total: int


class ArticulosResponse(Schema):
    """Response schema for articulos list endpoint."""

    articulos: list[ArticuloOut]
    total: int


class ProyectoLeyFilters(Schema):
    """Query filters for proyectos de ley."""

    page_size: int = 100
    offset: int = 0
    camara_origen: str | None = None
    etapa: int | None = None
    urgencia_actual: str | None = None


class ArticuloFilters(Schema):
    """Query filters for articulos."""

    page_size: int = 100
    offset: int = 0
    proyecto_id: str | None = None
    tipo: str | None = None


router = Router(auth=None)  # Public endpoint - no authentication required


@router.get("/", response=ProyectosLeyResponse)
async def list_proyectos_ley(request, filters: ProyectoLeyFilters = Query(...)):  # noqa: B008
    """
    List all proyectos de ley.

    - Ordered by fecha descending (most recent first)
    - Page size = 100 by default
    - Optional filters: camara_origen, etapa, urgencia_actual
    """
    queryset = ProyectoLey.objects.all()

    if filters.camara_origen:
        queryset = queryset.filter(camara_origen=filters.camara_origen)
    if filters.etapa is not None:
        queryset = queryset.filter(etapa=filters.etapa)
    if filters.urgencia_actual:
        queryset = queryset.filter(urgencia_actual=filters.urgencia_actual)

    total = await queryset.acount()
    proyectos_qs = queryset[filters.offset : filters.offset + filters.page_size]

    proyectos = []
    async for proyecto in proyectos_qs:
        articulos_count = await proyecto.articulos.acount()
        proyectos.append(
            ProyectoLeyOut(
                id=proyecto.id,
                proyecto_id=proyecto.proyecto_id,
                titulo=proyecto.titulo,
                camara_origen=proyecto.camara_origen,
                tipo_proyecto=proyecto.tipo_proyecto,
                etapa=proyecto.etapa,
                urgencia_actual=proyecto.urgencia_actual,
                fecha=proyecto.fecha.isoformat(),
                articulos_count=articulos_count,
            )
        )

    return ProyectosLeyResponse(proyectos=proyectos, total=total)


@router.get("/{proyecto_id}", response=ProyectoLeyDetailOut)
async def get_proyecto_ley(request, proyecto_id: str):
    """
    Get a specific proyecto de ley by its proyecto_id.

    Returns the proyecto with all its articulos.
    """
    from django.http import Http404

    try:
        proyecto = await ProyectoLey.objects.aget(proyecto_id=proyecto_id)
    except ProyectoLey.DoesNotExist:
        raise Http404(f"Proyecto {proyecto_id} not found")

    articulos = []
    async for articulo in proyecto.articulos.all():
        articulos.append(
            ArticuloOut(
                id=articulo.id,
                numero=articulo.numero,
                tipo=articulo.tipo,
                texto=articulo.texto,
                descripcion_semantica=articulo.descripcion_semantica,
            )
        )

    return ProyectoLeyDetailOut(
        id=proyecto.id,
        proyecto_id=proyecto.proyecto_id,
        titulo=proyecto.titulo,
        camara_origen=proyecto.camara_origen,
        tipo_proyecto=proyecto.tipo_proyecto,
        etapa=proyecto.etapa,
        urgencia_actual=proyecto.urgencia_actual,
        fecha=proyecto.fecha.isoformat(),
        articulos=articulos,
    )


@router.get("/articulos/", response=ArticulosResponse)
async def list_articulos(request, filters: ArticuloFilters = Query(...)):  # noqa: B008
    """
    List articulos with optional filters.

    - Page size = 100 by default
    - Optional filters: proyecto_id, tipo
    """
    queryset = Articulo.objects.select_related("proyecto").all()

    if filters.proyecto_id:
        queryset = queryset.filter(proyecto__proyecto_id=filters.proyecto_id)
    if filters.tipo:
        queryset = queryset.filter(tipo=filters.tipo)

    total = await queryset.acount()
    articulos_qs = queryset[filters.offset : filters.offset + filters.page_size]

    articulos = []
    async for articulo in articulos_qs:
        articulos.append(
            ArticuloOut(
                id=articulo.id,
                numero=articulo.numero,
                tipo=articulo.tipo,
                texto=articulo.texto,
                descripcion_semantica=articulo.descripcion_semantica,
            )
        )

    return ArticulosResponse(articulos=articulos, total=total)
