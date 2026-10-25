"""La base de pruebas hereda la configuración de producción y nunca es una base real (02-01)."""
from django.db import connection
from django.test import TestCase

BASES_REALES = {'manzagrafica_local', 'manzagrafica_replica'}


class EntornoBaseDePruebasTests(TestCase):
    def consultar(self, sql):
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()[0]

    def test_nombre_de_la_base_de_pruebas(self):
        nombre = self.consultar('SELECT DATABASE()')
        self.assertEqual(nombre, 'test_manzagrafica')
        self.assertNotIn(nombre, BASES_REALES)

    def test_juego_de_caracteres_y_colacion(self):
        # Valores de la línea base de producción (linea-base-produccion.md, sección 5).
        self.assertEqual(self.consultar('SELECT @@character_set_database'), 'utf8mb4')
        self.assertEqual(self.consultar('SELECT @@collation_database'), 'utf8mb4_unicode_ci')

    def test_zona_horaria_utc(self):
        self.assertIn(self.consultar('SELECT @@global.time_zone'), {'UTC', '+00:00'})
        self.assertIn(self.consultar('SELECT @@session.time_zone'), {'UTC', '+00:00'})

    def test_modo_sql_igual_a_produccion(self):
        # Decisión 02-01 (opción A, AUD-02-020): sin modo estricto, como producción.
        self.assertEqual(self.consultar('SELECT @@session.sql_mode'), 'NO_ENGINE_SUBSTITUTION')
