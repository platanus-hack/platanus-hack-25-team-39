"""Models for conflict_detector app."""

from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class Documento(models.Model):
    """Representa un documento cargado para análisis."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documentos",
        help_text="Usuario que subió el documento"
    )
    nombre = models.CharField(max_length=255)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conflict_detector_documento"
        ordering = ["-fecha_carga"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self) -> str:
        return f"{self.nombre}"


class DescubrimientoConflicto(models.Model):
    """Representa un descubrimiento de conflicto entre un documento y un proyecto de ley."""

    class Estado(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        TRACKING = "TRACKING", "En Seguimiento"
        DISCARDED = "DISCARDED", "Descartado"

    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name="descubrimientos",
    )
    proyecto_id = models.CharField(max_length=50)
    proyecto_titulo = models.TextField()
    max_nivel_relevancia = models.IntegerField(
        default=0,
        help_text="Nivel máximo de relevancia entre todos los impactos (0-100)"
    )
    descripcion_impacto_consolidada = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDING,
        help_text="Estado del descubrimiento: Pendiente, En Seguimiento o Descartado"
    )
    fecha_analisis = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conflict_detector_descubrimiento_conflicto"
        ordering = ["-fecha_analisis"]
        verbose_name = "Descubrimiento de Conflicto"
        verbose_name_plural = "Descubrimientos de Conflictos"

    def __str__(self) -> str:
        return f"{self.proyecto_id} - {self.documento.nombre}"


class ImpactoDescubierto(models.Model):
    """Representa un impacto individual descubierto dentro de un descubrimiento."""

    descubrimiento = models.ForeignKey(
        DescubrimientoConflicto,
        on_delete=models.CASCADE,
        related_name="impactos",
    )
    articulo_numero = models.IntegerField(
        help_text="Número del artículo de ley que genera el conflicto"
    )
    extracto_interno = models.TextField(
        help_text="Extracto del documento interno que presenta conflicto"
    )
    extracto_articulo = models.TextField(
        help_text="Extracto del artículo de ley que genera el conflicto"
    )
    nivel_relevancia = models.IntegerField(
        help_text="Nivel de relevancia del impacto (0-100)"
    )
    descripcion_impacto = models.TextField(
        help_text="Análisis técnico-legal del impacto"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conflict_detector_impacto_descubierto"
        ordering = ["-nivel_relevancia"]
        verbose_name = "Impacto Descubierto"
        verbose_name_plural = "Impactos Descubiertos"

    def __str__(self) -> str:
        return f"Impacto (relevancia: {self.nivel_relevancia})"


class EmbeddingCache(models.Model):
    """Cache de embeddings para evitar llamadas redundantes a la API de OpenAI."""

    text_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Hash SHA256 del texto original",
    )
    embedding = VectorField(
        dimensions=1536,
        help_text="Vector de embedding generado por OpenAI",
    )
    model_name = models.CharField(
        max_length=100,
        default="text-embedding-3-small",
        help_text="Nombre del modelo de embedding utilizado",
    )
    dimension = models.IntegerField(
        default=1536,
        help_text="Dimensión del vector de embedding",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conflict_detector_embedding_cache"
        verbose_name = "Embedding Cache"
        verbose_name_plural = "Embedding Caches"
        indexes = [
            models.Index(fields=["text_hash", "model_name"]),
        ]

    def __str__(self) -> str:
        return f"Embedding {self.text_hash[:8]}... ({self.model_name})"
