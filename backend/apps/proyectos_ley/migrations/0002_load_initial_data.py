"""Load initial data from JSON files."""

import json
from datetime import datetime
from pathlib import Path

from django.db import migrations


def load_proyectos_ley(apps, schema_editor):
    """Load proyectos de ley from JSON files in data/proyectos_ley/."""
    ProyectoLey = apps.get_model("proyectos_ley", "ProyectoLey")
    Articulo = apps.get_model("proyectos_ley", "Articulo")

    # Get the data directory path
    data_dir = (
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "proyectos_ley"
    )

    if not data_dir.exists():
        print(f"Warning: Data directory not found: {data_dir}")
        return

    # Load all JSON files
    json_files = sorted(data_dir.glob("*.json"))

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Create or update ProyectoLey
        proyecto, created = ProyectoLey.objects.update_or_create(
            proyecto_id=data["id"],
            defaults={
                "titulo": data["titulo"],
                "camara_origen": data["camara_origen"],
                "tipo_proyecto": data["tipo_proyecto"],
                "etapa": data["etapa"],
                "urgencia_actual": data["urgencia_actual"],
                "fecha": datetime.strptime(data["fecha"], "%Y-%m-%d").date(),
            },
        )

        # Create Articulos
        for articulo_data in data.get("articulos", []):
            Articulo.objects.update_or_create(
                proyecto=proyecto,
                numero=articulo_data["numero"],
                defaults={
                    "tipo": articulo_data.get("tipo", "permanente"),
                    "texto": articulo_data["texto"],
                    "descripcion_semantica": articulo_data["descripcion_semantica"],
                },
            )

        action = "Created" if created else "Updated"
        print(
            f"{action} proyecto: {data['id']} with {len(data.get('articulos', []))} articulos"
        )


def reverse_load(apps, schema_editor):
    """Remove all loaded data."""
    ProyectoLey = apps.get_model("proyectos_ley", "ProyectoLey")
    ProyectoLey.objects.all().delete()


class Migration(migrations.Migration):
    """Load initial proyectos de ley data."""

    dependencies = [
        ("proyectos_ley", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_proyectos_ley, reverse_load),
    ]
