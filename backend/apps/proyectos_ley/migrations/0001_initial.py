"""Initial migration for proyectos_ley app."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Create ProyectoLey and Articulo tables."""

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProyectoLey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "proyecto_id",
                    models.CharField(
                        help_text="Identificador único del proyecto (ej: 12058-08)",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "titulo",
                    models.TextField(
                        help_text="Título descriptivo del proyecto de ley"
                    ),
                ),
                (
                    "camara_origen",
                    models.CharField(
                        help_text="Cámara de origen (Senado o Cámara de Diputados)",
                        max_length=100,
                    ),
                ),
                (
                    "tipo_proyecto",
                    models.CharField(
                        help_text="Tipo de proyecto (ej: Proyecto de Ley)",
                        max_length=100,
                    ),
                ),
                (
                    "etapa",
                    models.IntegerField(help_text="Etapa legislativa actual (1-3)"),
                ),
                (
                    "urgencia_actual",
                    models.CharField(
                        help_text="Nivel de urgencia (Sin urgencia, Discusión inmediata, etc.)",
                        max_length=100,
                    ),
                ),
                (
                    "fecha",
                    models.DateField(help_text="Fecha de presentación del proyecto"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Proyecto de Ley",
                "verbose_name_plural": "Proyectos de Ley",
                "db_table": "proyectos_ley_proyecto",
                "ordering": ["-fecha"],
            },
        ),
        migrations.CreateModel(
            name="Articulo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "numero",
                    models.IntegerField(
                        help_text="Número del artículo dentro del proyecto"
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        default="permanente",
                        help_text="Tipo de artículo (permanente, transitorio, etc.)",
                        max_length=50,
                    ),
                ),
                (
                    "texto",
                    models.TextField(help_text="Texto completo del artículo"),
                ),
                (
                    "descripcion_semantica",
                    models.TextField(
                        help_text="Descripción semántica para búsqueda y embeddings"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "proyecto",
                    models.ForeignKey(
                        help_text="Proyecto de ley al que pertenece el artículo",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="articulos",
                        to="proyectos_ley.proyectoley",
                    ),
                ),
            ],
            options={
                "verbose_name": "Artículo",
                "verbose_name_plural": "Artículos",
                "db_table": "proyectos_ley_articulo",
                "ordering": ["proyecto", "numero"],
                "unique_together": {("proyecto", "numero")},
            },
        ),
    ]
