"""API endpoints para conflict detector."""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from ninja import File, Router, UploadedFile

from .models import Documento, DescubrimientoConflicto
from apps.proyectos_ley.models import ProyectoLey
from .schemas import (
    DescubrimientoDetailSchema,
    DescubrimientoListSchema,
    DocumentoDetailSchema,
    DocumentoListSchema,
)
from .services import detect_conflicts


router = Router()


@router.post("/detect")
async def detect_conflicts_endpoint(request, file: UploadedFile = File(...)):
    """
    Detecta conflictos usando el agente LangGraph.

    Recibe un archivo PDF y retorna el resultado del análisis del agente.
    Crea un descubrimiento de conflictos con los impactos detectados en la base de datos.

    Returns:
        Diccionario con descubrimiento_id, fecha_analisis, nombre_documento e impactos
    """
    # Leer el contenido del archivo PDF (read() es síncrono, no necesita await)
    pdf_content = file.read()

    # Procesar el PDF y detectar conflictos (guarda automáticamente en DB)
    result = await detect_conflicts(pdf_content, nombre_documento=file.name, user=request.user)
    return result


@router.get("/documents", response=list[DocumentoListSchema])
def list_documents(request):
    """
    Lista todos los documentos cargados por el usuario actual.

    Returns:
        Lista de documentos con su información básica y cantidad de descubrimientos
    """
    documentos = Documento.objects.filter(user=request.user).annotate(
        cantidad_descubrimientos=Count("descubrimientos")
    ).all()

    return [
        {
            "id": doc.id,
            "nombre": doc.nombre,
            "fecha_carga": doc.fecha_carga,
            "cantidad_descubrimientos": doc.cantidad_descubrimientos,
        }
        for doc in documentos
    ]


@router.get("/documents/{documento_id}", response=DocumentoDetailSchema)
def get_document_detail(request, documento_id: int):
    """
    Obtiene los detalles de un documento específico con todos sus descubrimientos.

    Args:
        documento_id: ID del documento a consultar

    Returns:
        Documento con todos sus descubrimientos e impactos
    """
    documento = get_object_or_404(
        Documento.objects.filter(user=request.user).prefetch_related(
            "descubrimientos__impactos"
        ),
        id=documento_id,
    )

    return {
        "id": documento.id,
        "nombre": documento.nombre,
        "fecha_carga": documento.fecha_carga,
        "descubrimientos": [
            {
                "id": desc.id,
                "proyecto_id": desc.proyecto_id,
                "proyecto_titulo": desc.proyecto_titulo,
                "descripcion_impacto_consolidada": desc.descripcion_impacto_consolidada,
                "fecha_analisis": desc.fecha_analisis,
                "impactos": [
                    {
                        "id": imp.id,
                        "extracto_interno": imp.extracto_interno,
                        "extracto_articulo": imp.extracto_articulo,
                        "nivel_relevancia": imp.nivel_relevancia,
                        "descripcion_impacto": imp.descripcion_impacto,
                        "created_at": imp.created_at,
                    }
                    for imp in desc.impactos.all()
                ],
            }
            for desc in documento.descubrimientos.all()
        ],
    }


@router.delete("/documents/{documento_id}")
def delete_document(request, documento_id: int):
    """
    Elimina un documento y todos sus descubrimientos asociados.

    Args:
        documento_id: ID del documento a eliminar

    Returns:
        Mensaje de confirmación
    """
    documento = get_object_or_404(Documento, id=documento_id, user=request.user)
    nombre = documento.nombre
    documento.delete()

    return {"success": True, "message": f"Documento '{nombre}' eliminado correctamente"}


@router.get("/discoveries", response=list[DescubrimientoListSchema])
def list_discoveries(request):
    """
    Lista todos los descubrimientos de conflictos pendientes del usuario actual.
    Excluye los descubrimientos descartados y los que están en seguimiento.

    Returns:
        Lista de descubrimientos con información básica y cantidad de impactos
    """
    descubrimientos = (
        DescubrimientoConflicto.objects.select_related("documento")
        .filter(documento__user=request.user, estado=DescubrimientoConflicto.Estado.PENDING)
        .annotate(cantidad_impactos=Count("impactos"))
        .order_by("-max_nivel_relevancia")
    )

    return [
        {
            "id": desc.id,
            "proyecto_id": desc.proyecto_id,
            "proyecto_titulo": desc.proyecto_titulo,
            "descripcion_impacto_consolidada": desc.descripcion_impacto_consolidada,
            "fecha_analisis": desc.fecha_analisis,
            "cantidad_impactos": desc.cantidad_impactos,
            "max_nivel_relevancia": desc.max_nivel_relevancia,
            "documento_nombre": desc.documento.nombre,
            "documento_id": desc.documento.id,
            "estado": desc.estado,
        }
        for desc in descubrimientos
    ]


@router.get("/discoveries/tracking", response=list[DescubrimientoListSchema])
def list_tracking_discoveries(request):
    """
    Lista todos los descubrimientos que están en seguimiento del usuario actual.
    Incluye información del proyecto de ley (etapa, fecha, etc.)

    Returns:
        Lista de descubrimientos en seguimiento con información básica y cantidad de impactos
    """
    descubrimientos = (
        DescubrimientoConflicto.objects.select_related("documento")
        .filter(documento__user=request.user, estado=DescubrimientoConflicto.Estado.TRACKING)
        .annotate(cantidad_impactos=Count("impactos"))
    )

    result = []
    for desc in descubrimientos:
        # Intentar obtener el proyecto de ley relacionado
        try:
            proyecto_ley = ProyectoLey.objects.get(proyecto_id=desc.proyecto_id)
            proyecto_etapa = proyecto_ley.etapa
            proyecto_fecha = proyecto_ley.fecha
            proyecto_camara_origen = proyecto_ley.camara_origen
        except ProyectoLey.DoesNotExist:
            # Si no existe el proyecto, usar valores por defecto
            proyecto_etapa = 1
            proyecto_fecha = desc.fecha_analisis.date()
            proyecto_camara_origen = ""

        result.append({
            "id": desc.id,
            "proyecto_id": desc.proyecto_id,
            "proyecto_titulo": desc.proyecto_titulo,
            "descripcion_impacto_consolidada": desc.descripcion_impacto_consolidada,
            "fecha_analisis": desc.fecha_analisis,
            "cantidad_impactos": desc.cantidad_impactos,
            "max_nivel_relevancia": desc.max_nivel_relevancia,
            "documento_nombre": desc.documento.nombre,
            "documento_id": desc.documento.id,
            "estado": desc.estado,
            "proyecto_etapa": proyecto_etapa,
            "proyecto_fecha": proyecto_fecha.isoformat() if proyecto_fecha else None,
            "proyecto_camara_origen": proyecto_camara_origen,
        })

    return result


@router.get("/discoveries/{descubrimiento_id}", response=DescubrimientoDetailSchema)
def get_discovery_detail(request, descubrimiento_id: int):
    """
    Obtiene los detalles de un descubrimiento específico con todos sus impactos.

    Args:
        descubrimiento_id: ID del descubrimiento a consultar

    Returns:
        Descubrimiento con todos sus impactos y el documento asociado
    """
    descubrimiento = get_object_or_404(
        DescubrimientoConflicto.objects.select_related("documento").prefetch_related(
            "impactos"
        ).filter(documento__user=request.user),
        id=descubrimiento_id,
    )

    return {
        "id": descubrimiento.id,
        "proyecto_id": descubrimiento.proyecto_id,
        "proyecto_titulo": descubrimiento.proyecto_titulo,
        "descripcion_impacto_consolidada": descubrimiento.descripcion_impacto_consolidada,
        "fecha_analisis": descubrimiento.fecha_analisis,
        "estado": descubrimiento.estado,
        "max_nivel_relevancia": descubrimiento.max_nivel_relevancia,
        "documento": {
            "id": descubrimiento.documento.id,
            "nombre": descubrimiento.documento.nombre,
            "fecha_carga": descubrimiento.documento.fecha_carga,
            "cantidad_descubrimientos": descubrimiento.documento.descubrimientos.count(),
        },
        "impactos": [
            {
                "id": imp.id,
                "articulo_numero": imp.articulo_numero,
                "extracto_interno": imp.extracto_interno,
                "extracto_articulo": imp.extracto_articulo,
                "nivel_relevancia": imp.nivel_relevancia,
                "descripcion_impacto": imp.descripcion_impacto,
                "created_at": imp.created_at,
            }
            for imp in descubrimiento.impactos.all()
        ],
    }


@router.post("/discoveries/{descubrimiento_id}/track")
def track_discovery(request, descubrimiento_id: int):
    """
    Marca un descubrimiento como en seguimiento.
    El descubrimiento dejará de aparecer en la vista de descubrimientos
    y comenzará a aparecer en la vista de seguimiento.

    Args:
        descubrimiento_id: ID del descubrimiento a marcar como en seguimiento

    Returns:
        Mensaje de confirmación con el descubrimiento actualizado
    """
    descubrimiento = get_object_or_404(
        DescubrimientoConflicto,
        id=descubrimiento_id,
        documento__user=request.user
    )
    descubrimiento.estado = DescubrimientoConflicto.Estado.TRACKING
    descubrimiento.save()

    return {
        "success": True,
        "message": f"Descubrimiento '{descubrimiento.proyecto_id}' marcado como en seguimiento",
        "estado": descubrimiento.estado,
    }


@router.post("/discoveries/{descubrimiento_id}/discard")
def discard_discovery(request, descubrimiento_id: int):
    """
    Marca un descubrimiento como descartado.
    El descubrimiento dejará de aparecer en la vista de descubrimientos.

    Args:
        descubrimiento_id: ID del descubrimiento a descartar

    Returns:
        Mensaje de confirmación con el descubrimiento actualizado
    """
    descubrimiento = get_object_or_404(
        DescubrimientoConflicto,
        id=descubrimiento_id,
        documento__user=request.user
    )
    descubrimiento.estado = DescubrimientoConflicto.Estado.DISCARDED
    descubrimiento.save()

    return {
        "success": True,
        "message": f"Descubrimiento '{descubrimiento.proyecto_id}' descartado",
        "estado": descubrimiento.estado,
    }


@router.post("/demo/advance-time")
def advance_time(request):
    """
    Avanza las etapas de los proyectos de ley en seguimiento (para demo).
    Incrementa la etapa de cada proyecto en 1 (máximo 4).

    Returns:
        Mensaje de confirmación con cantidad de proyectos actualizados
    """
    # Obtener todos los proyectos que tienen descubrimientos en seguimiento
    descubrimientos_tracking = DescubrimientoConflicto.objects.filter(
        documento__user=request.user,
        estado=DescubrimientoConflicto.Estado.TRACKING
    ).values_list('proyecto_id', flat=True).distinct()

    proyectos_actualizados = 0
    for proyecto_id in descubrimientos_tracking:
        try:
            proyecto = ProyectoLey.objects.get(proyecto_id=proyecto_id)
            if proyecto.etapa < 4:
                proyecto.etapa += 1
                proyecto.save()
                proyectos_actualizados += 1
        except ProyectoLey.DoesNotExist:
            continue

    return {
        "success": True,
        "message": f"Se avanzó la etapa de {proyectos_actualizados} proyecto(s)",
        "proyectos_actualizados": proyectos_actualizados,
    }
