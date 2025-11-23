"""Admin para conflict_detector."""

from django.contrib import admin

from .models import (
    Documento,
    DescubrimientoConflicto,
    EmbeddingCache,
    ImpactoDescubierto,
)


class DescubrimientoConflictoInline(admin.TabularInline):
    """Inline para mostrar descubrimientos dentro del documento."""

    model = DescubrimientoConflicto
    extra = 0
    readonly_fields = [
        "proyecto_id",
        "proyecto_titulo",
        "descripcion_impacto_consolidada",
        "fecha_analisis",
    ]
    show_change_link = True


class ImpactoDescubiertoInline(admin.TabularInline):
    """Inline para mostrar impactos dentro del descubrimiento."""

    model = ImpactoDescubierto
    extra = 0
    readonly_fields = [
        "extracto_interno",
        "extracto_articulo",
        "nivel_relevancia",
        "descripcion_impacto",
        "created_at",
    ]


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """Admin para Documento."""

    list_display = ["id", "nombre", "user", "fecha_carga", "cantidad_descubrimientos"]
    list_filter = ["fecha_carga", "user"]
    search_fields = ["nombre", "user__email"]
    readonly_fields = ["fecha_carga", "created_at", "updated_at"]
    inlines = [DescubrimientoConflictoInline]

    def cantidad_descubrimientos(self, obj):
        return obj.descubrimientos.count()

    cantidad_descubrimientos.short_description = "Descubrimientos"


@admin.register(DescubrimientoConflicto)
class DescubrimientoConflictoAdmin(admin.ModelAdmin):
    """Admin para DescubrimientoConflicto."""

    list_display = [
        "id",
        "documento",
        "proyecto_id",
        "proyecto_titulo_corto",
        "fecha_analisis",
        "cantidad_impactos",
    ]
    list_filter = ["fecha_analisis", "documento"]
    search_fields = ["proyecto_id", "proyecto_titulo", "documento__nombre"]
    readonly_fields = ["fecha_analisis", "created_at", "updated_at"]
    inlines = [ImpactoDescubiertoInline]

    def proyecto_titulo_corto(self, obj):
        return (
            obj.proyecto_titulo[:50] + "..."
            if len(obj.proyecto_titulo) > 50
            else obj.proyecto_titulo
        )

    proyecto_titulo_corto.short_description = "Proyecto"

    def cantidad_impactos(self, obj):
        return obj.impactos.count()

    cantidad_impactos.short_description = "Impactos"


@admin.register(ImpactoDescubierto)
class ImpactoDescubiertoAdmin(admin.ModelAdmin):
    """Admin para ImpactoDescubierto."""

    list_display = [
        "id",
        "descubrimiento",
        "nivel_relevancia",
        "descripcion_corta",
    ]
    list_filter = ["nivel_relevancia", "descubrimiento__documento"]
    search_fields = ["descripcion_impacto", "extracto_interno", "extracto_articulo"]
    readonly_fields = ["created_at", "updated_at"]

    def descripcion_corta(self, obj):
        return (
            obj.descripcion_impacto[:80] + "..."
            if len(obj.descripcion_impacto) > 80
            else obj.descripcion_impacto
        )

    descripcion_corta.short_description = "Descripcion"


@admin.register(EmbeddingCache)
class EmbeddingCacheAdmin(admin.ModelAdmin):
    """Admin para EmbeddingCache."""

    list_display = [
        "id",
        "text_hash_corto",
        "model_name",
        "dimension",
        "created_at",
    ]
    list_filter = ["model_name", "dimension", "created_at"]
    search_fields = ["text_hash"]
    readonly_fields = ["text_hash", "embedding", "model_name", "dimension", "created_at"]

    def text_hash_corto(self, obj):
        return f"{obj.text_hash[:16]}..."

    text_hash_corto.short_description = "Hash"
