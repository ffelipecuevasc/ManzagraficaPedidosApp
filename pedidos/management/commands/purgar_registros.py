from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pedidos.eventos import RETENCION_EVENTOS_DIAS, limite_retencion, purgar_eventos


class Command(BaseCommand):
    help = 'Elimina los eventos de negocio más antiguos que la retención.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias', type=int, default=RETENCION_EVENTOS_DIAS,
            help=f'Días de retención (por defecto {RETENCION_EVENTOS_DIAS}).',
        )

    def handle(self, *args, **opciones):
        dias = opciones['dias']
        if dias < 1:
            raise CommandError('La retención debe ser de al menos 1 día.')
        ahora = timezone.now()
        limite = timezone.localtime(limite_retencion(dias, ahora))
        eliminados = purgar_eventos(dias, ahora)
        self.stdout.write(
            f'Eventos eliminados: {eliminados} '
            f'(anteriores al {limite:%d-%m-%Y %H:%M}, hora de Chile; retención de {dias} días).'
        )
