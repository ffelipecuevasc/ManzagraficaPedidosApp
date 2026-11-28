# Iteración 14-04: solo el índice único de `folio` (Clase 2, aditiva). Debe emitir únicamente
# ADD CONSTRAINT ... UNIQUE; si sqlmigrate muestra un MODIFY de la columna, es Clase 3: se detiene.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pedidos", "0011_folio_igual_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cotizacion",
            name="folio",
            field=models.PositiveIntegerField(editable=False, unique=True, verbose_name="Folio"),
        ),
    ]
