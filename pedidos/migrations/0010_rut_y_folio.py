# Iteración 14-04 (RDA-024), escrita a mano para separar los pasos (opción C, 2026-11-20).
# Clase 2, aditiva: tabla nueva y dos columnas nuevas que nacen NOT NULL con su relleno en el mismo
# ALTER. `folio` nace sin índice único: todas las filas comparten el valor transitorio 0 hasta la
# 0011; el índice va solo en la 0012. Se confirma con sqlmigrate.

import pedidos.validadores
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pedidos", "0009_acceso_bloqueado"),
    ]

    operations = [
        migrations.CreateModel(
            name="SecuenciaFolio",
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
                ("nombre", models.CharField(max_length=30, unique=True)),
                ("ultimo_folio", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Secuencia de folios",
                "verbose_name_plural": "Secuencias de folios",
            },
        ),
        migrations.AddField(
            model_name="cotizacion",
            name="folio",
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name="Folio"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cliente",
            name="rut",
            field=models.CharField(
                default="00.000.000-0",
                help_text="Con o sin puntos y guion. Ej: 12.345.678-5",
                max_length=12,
                validators=[pedidos.validadores.validar_rut],
                verbose_name="RUT",
            ),
            preserve_default=False,
        ),
    ]
