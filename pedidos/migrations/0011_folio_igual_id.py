# Iteración 14-04: datos, sin DDL. Las cotizaciones existentes reciben folio = id (D3) y el
# contador de folios parte en el mayor folio (0 si no hay cotizaciones). Reversa definida: deja el
# valor transitorio 0 y borra la fila del contador. El número inicial del negocio no va aquí (D4).

from django.db import migrations
from django.db.models import F, Max

NOMBRE = "cotizacion"


def folio_igual_id(apps, schema_editor):
    Cotizacion = apps.get_model("pedidos", "Cotizacion")
    SecuenciaFolio = apps.get_model("pedidos", "SecuenciaFolio")
    Cotizacion.objects.update(folio=F("id"))
    mayor = Cotizacion.objects.aggregate(m=Max("folio"))["m"] or 0
    SecuenciaFolio.objects.update_or_create(nombre=NOMBRE, defaults={"ultimo_folio": mayor})


def deshacer(apps, schema_editor):
    Cotizacion = apps.get_model("pedidos", "Cotizacion")
    SecuenciaFolio = apps.get_model("pedidos", "SecuenciaFolio")
    Cotizacion.objects.update(folio=0)
    SecuenciaFolio.objects.filter(nombre=NOMBRE).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pedidos", "0010_rut_y_folio"),
    ]

    operations = [
        migrations.RunPython(folio_igual_id, deshacer),
    ]
