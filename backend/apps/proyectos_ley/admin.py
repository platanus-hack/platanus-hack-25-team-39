"""Admin configuration for proyectos_ley app."""

from django.contrib import admin

from .models import Articulo, ProyectoLey


class ArticuloInline(admin.TabularInline):
    """Inline admin for Articulo model."""

    model = Articulo
    extra = 0
    fields = ("numero", "tipo", "descripcion_semantica")
    readonly_fields = ("numero",)
    show_change_link = True


@admin.register(ProyectoLey)
class ProyectoLeyAdmin(admin.ModelAdmin):
    """Admin configuration for ProyectoLey model."""

    list_display = (
        "proyecto_id",
        "titulo_truncado",
        "camara_origen",
        "etapa",
        "urgencia_actual",
        "fecha",
        "articulos_count",
    )
    list_filter = ("camara_origen", "etapa", "urgencia_actual")
    search_fields = ("proyecto_id", "titulo")
    ordering = ("-fecha",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ArticuloInline]

    fieldsets = (
        (None, {"fields": ("proyecto_id", "titulo")}),
        (
            "Información Legislativa",
            {"fields": ("camara_origen", "tipo_proyecto", "etapa", "urgencia_actual", "fecha")},
        ),
        ("Metadatos", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def titulo_truncado(self, obj):
        """Return truncated title."""
        return obj.titulo[:60] + "..." if len(obj.titulo) > 60 else obj.titulo

    titulo_truncado.short_description = "Título"

    def articulos_count(self, obj):
        """Return count of articulos."""
        return obj.articulos.count()

    articulos_count.short_description = "Artículos"


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    """Admin configuration for Articulo model."""

    list_display = ("__str__", "proyecto", "numero", "tipo")
    list_filter = ("tipo", "proyecto")
    search_fields = ("texto", "descripcion_semantica", "proyecto__proyecto_id")
    ordering = ("proyecto", "numero")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("proyecto", "numero", "tipo")}),
        ("Contenido", {"fields": ("texto", "descripcion_semantica")}),
        ("Metadatos", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
