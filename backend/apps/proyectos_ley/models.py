"""Models for proyectos_ley app."""

from django.db import models


class ProyectoLey(models.Model):
    """Modelo Django para representar un proyecto de ley."""

    proyecto_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único del proyecto (ej: 12058-08)",
    )
    titulo = models.TextField(help_text="Título descriptivo del proyecto de ley")
    camara_origen = models.CharField(
        max_length=100,
        help_text="Cámara de origen (Senado o Cámara de Diputados)",
    )
    tipo_proyecto = models.CharField(
        max_length=100,
        help_text="Tipo de proyecto (ej: Proyecto de Ley)",
    )
    etapa = models.IntegerField(help_text="Etapa legislativa actual (1-3)")
    urgencia_actual = models.CharField(
        max_length=100,
        help_text="Nivel de urgencia (Sin urgencia, Discusión inmediata, etc.)",
    )
    fecha = models.DateField(help_text="Fecha de presentación del proyecto")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "proyectos_ley_proyecto"
        verbose_name = "Proyecto de Ley"
        verbose_name_plural = "Proyectos de Ley"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.proyecto_id} - {self.titulo[:50]}"


class Articulo(models.Model):
    """Modelo Django para representar un artículo de un proyecto de ley."""

    proyecto = models.ForeignKey(
        ProyectoLey,
        on_delete=models.CASCADE,
        related_name="articulos",
        help_text="Proyecto de ley al que pertenece el artículo",
    )
    numero = models.IntegerField(help_text="Número del artículo dentro del proyecto")
    tipo = models.CharField(
        max_length=50,
        default="permanente",
        help_text="Tipo de artículo (permanente, transitorio, etc.)",
    )
    texto = models.TextField(help_text="Texto completo del artículo")
    descripcion_semantica = models.TextField(
        help_text="Descripción semántica para búsqueda y embeddings"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "proyectos_ley_articulo"
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ["proyecto", "numero"]
        unique_together = [["proyecto", "numero"]]

    def __str__(self) -> str:
        return f"Art. {self.numero} - {self.proyecto.proyecto_id}"
