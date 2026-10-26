"""Lógica de dinero: pruebas de caracterización (iteración 02-02).

Congelan cómo calcula HOY la aplicación el IVA, los saldos, el abono inicial y las cifras
del panel, sea correcto o no. Lo que el cliente no ha confirmado lleva PENDIENTE_CLIENTE
(registro-pendientes.md, sección 2). Corregir cualquier regla queda fuera de esta iteración.
"""
import tempfile
from collections import Counter
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from pedidos import views
from pedidos.forms import PedidoForm
from pedidos.models import HistorialBD, Pago, Pedido

from .factorias import (
    crear_cliente, crear_cotizacion, crear_item_pedido, crear_pago, crear_pedido,
    crear_producto, crear_usuario, momento_chile,
)


def iva_comercial(valor_neto):
    """Oráculo independiente: 19 % con Decimal y redondeo comercial (mitad hacia arriba)."""
    return int((Decimal(valor_neto) * Decimal('0.19')).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


# Decisión D3: hora congelada al mediodía de Chile, lejos de los bordes de día y de mes
# (los bordes en UTC son AUD-02-003 y se prueban en 02-04).
AHORA = momento_chile(2026, 10, 15)


def congelar_hora():
    """Las vistas y `registrar_metricas_diarias` leen la hora con `timezone.now()` del módulo."""
    return mock.patch('django.utils.timezone.now', return_value=AHORA)


# ---------------------------------------------------------------------------
# Tarea 1 · IVA y valor bruto de Producto
# ---------------------------------------------------------------------------
class IvaProductoTests(TestCase):
    # (valor_neto, iva que guarda hoy el modelo). Se observaron al ejecutar y se fijan.
    CASOS = [
        (0, 0),
        (1, 0),
        (100, 19),
        (1_000, 190),
        (1_000_000, 190_000),
        (-1_000, -190),  # valor_neto no tiene validadores: el modelo acepta negativos.
        # valor_neto × 0,19 termina en ,5: el round de Python redondea al par.
        (50, 10),    # 9,5 → 10
        (150, 28),   # 28,5 → 28 (el redondeo comercial da 29)
        (250, 48),   # 47,5 → 48
        (350, 66),   # 66,5 → 66 (el redondeo comercial da 67)
        (4_950, 940),  # 940,5 → 940 (el redondeo comercial da 941)
    ]

    def test_iva_y_valor_bruto_guardados(self):
        for valor_neto, iva_esperado in self.CASOS:
            with self.subTest(valor_neto=valor_neto):
                producto = crear_producto(valor_neto=valor_neto)
                producto.refresh_from_db()
                self.assertEqual(producto.iva, iva_esperado)
                self.assertEqual(producto.valor_bruto, valor_neto + iva_esperado)

    def test_invariante_bruto_igual_neto_mas_iva(self):
        for valor_neto, _ in self.CASOS:
            with self.subTest(valor_neto=valor_neto):
                producto = crear_producto(valor_neto=valor_neto)
                self.assertEqual(producto.valor_bruto, producto.valor_neto + producto.iva)

    def test_recalcula_al_cambiar_valor_neto(self):
        producto = crear_producto(valor_neto=1_000)

        producto.valor_neto = 2_000
        producto.save()
        producto.refresh_from_db()

        self.assertEqual((producto.iva, producto.valor_bruto), (380, 2_380))

    def test_oraculo_comercial_difiere_solo_en_las_mitades_al_par(self):
        # Decisión D1: las diferencias se anotan en la bitácora; no son regresión.
        diferencias = {}
        for valor_neto, iva_modelo in self.CASOS:
            with self.subTest(valor_neto=valor_neto):
                diferencia = iva_comercial(valor_neto) - iva_modelo
                self.assertIn(diferencia, (0, 1))  # nunca más de un peso
                if diferencia:
                    diferencias[valor_neto] = diferencia
        self.assertEqual(diferencias, {150: 1, 350: 1, 4_950: 1})


# ---------------------------------------------------------------------------
# Tarea 2 · Pedido: total pagado, saldo y porcentaje
# ---------------------------------------------------------------------------
class SaldoPedidoTests(TestCase):
    # (descripción, valor_venta, montos de pagos, total pagado, saldo, porcentaje)
    CASOS = [
        ('sin pagos', 10_000, [], 0, 10_000, 0),
        ('un pago parcial', 10_000, [4_000], 4_000, 6_000, 40),
        ('varios pagos acumulados', 10_000, [2_000, 3_000, 1_500], 6_500, 3_500, 65),
        ('pago exacto del total', 10_000, [10_000], 10_000, 0, 100),
        # PENDIENTE_CLIENTE: ¿se permite el sobrepago? Hoy el saldo queda negativo y el
        # porcentaje pasa de 100.
        ('sobrepago', 10_000, [8_000, 4_000], 12_000, -2_000, 120),
        # PENDIENTE_CLIENTE: un pedido de $0, ¿cuenta como pagado al 100 %? Hoy sí.
        ('valor 0 sin pagos', 0, [], 0, 0, 100),
        ('valor 0 con un pago', 0, [5_000], 5_000, -5_000, 100),
        # El porcentaje se trunca (int), no se redondea.
        ('un tercio', 3_000, [1_000], 1_000, 2_000, 33),
        ('dos tercios', 3_000, [2_000], 2_000, 1_000, 66),
        ('99,9 %', 1_000, [999], 999, 1, 99),
        # Hallazgo propuesto: 29/100 en float da 28,999… y el truncado entrega 28, no 29.
        ('error de float al truncar', 100, [29], 29, 71, 28),
    ]

    def test_matriz_de_saldos(self):
        for descripcion, valor_venta, montos, total, saldo, porcentaje in self.CASOS:
            with self.subTest(descripcion):
                pedido = crear_pedido(valor_venta=valor_venta)
                for monto in montos:
                    crear_pago(pedido, monto=monto)

                self.assertEqual(pedido.total_pagado_real, total)
                self.assertEqual(pedido.saldo_pendiente, saldo)
                self.assertEqual(pedido.porcentaje_pagado, porcentaje)

    def test_pagos_de_otro_pedido_no_se_mezclan(self):
        pedido = crear_pedido(valor_venta=10_000)
        otro = crear_pedido(valor_venta=10_000)
        crear_pago(pedido, monto=1_000)
        crear_pago(otro, monto=7_000)

        self.assertEqual(pedido.total_pagado_real, 1_000)
        self.assertEqual(pedido.saldo_pendiente, 9_000)
        self.assertEqual(otro.total_pagado_real, 7_000)

    def test_monto_de_pago_no_admite_negativos_ni_decimales(self):
        pedido = crear_pedido(valor_venta=10_000)
        for monto in (-1, '1.5'):
            with self.subTest(monto=monto):
                pago = Pago(pedido=pedido, monto=monto)
                with self.assertRaises(ValidationError):
                    pago.full_clean()


# ---------------------------------------------------------------------------
# Tarea 3 · Ítems
# ---------------------------------------------------------------------------
class SubtotalItemsTests(TestCase):
    CASOS = [
        ('1', 10_000, Decimal('10000')),
        ('3', 2_500, Decimal('7500')),
        ('2.50', 1_000, Decimal('2500')),
        ('0.75', 3_333, Decimal('2499.75')),  # el subtotal no se redondea al peso
    ]

    def test_subtotal_item_pedido(self):
        for cantidad, precio, esperado in self.CASOS:
            with self.subTest(cantidad=cantidad, precio=precio):
                pedido = crear_pedido()
                item = crear_item_pedido(pedido, cantidad=cantidad, precio_unitario=precio)
                item.refresh_from_db()
                self.assertIsInstance(item.subtotal, Decimal)
                self.assertEqual(item.subtotal, esperado)

    def test_subtotal_item_cotizacion(self):
        for cantidad, precio, esperado in self.CASOS:
            with self.subTest(cantidad=cantidad, precio=precio):
                cotizacion = crear_cotizacion(items=[{'cantidad': cantidad, 'precio_unitario': precio}])
                item = cotizacion.items.get()
                self.assertIsInstance(item.subtotal, Decimal)
                self.assertEqual(item.subtotal, esperado)

    def test_valor_venta_distinto_de_la_suma_de_items_se_acepta(self):
        # PENDIENTE_CLIENTE (AUD-02-014): ¿el valor de venta debe ser igual a la suma de los
        # ítems? Hoy el modelo no los contrasta: el pedido se guarda con ambos valores.
        pedido = crear_pedido(valor_venta=5_000, items=[
            {'cantidad': '2', 'precio_unitario': 4_000},
            {'cantidad': '1.5', 'precio_unitario': 2_000},
        ])
        pedido.full_clean()
        pedido.refresh_from_db()

        suma_items = sum(item.subtotal for item in pedido.items.all())
        self.assertEqual(suma_items, Decimal('11000'))
        self.assertEqual(pedido.valor_venta, 5_000)
        self.assertEqual(pedido.saldo_pendiente, 5_000)  # el saldo usa valor_venta, no los ítems


# ---------------------------------------------------------------------------
# Tarea 4 · Abono inicial del formulario de pedido
# ---------------------------------------------------------------------------
class AbonoInicialTests(TestCase):
    MENSAJE = 'El abono inicial no puede ser mayor al valor total del pedido.'

    def setUp(self):
        self.cliente = crear_cliente()

    def formulario(self, valor_venta, abono):
        datos = {'cliente': self.cliente.pk, 'resumen_pedido': 'Pedido de prueba',
                 'valor_venta': valor_venta, 'abono_inicial': abono}
        return PedidoForm(data=datos)

    def test_valor_venta_se_limpia_antes_que_abono_inicial(self):
        # Condición de todos los casos: clean_abono_inicial lee cleaned_data['valor_venta'],
        # que solo existe si ese campo se limpió antes. Django limpia en el orden de los campos.
        campos = list(PedidoForm().fields)
        self.assertLess(campos.index('valor_venta'), campos.index('abono_inicial'))
        self.assertEqual(campos[-1], 'abono_inicial')

    def test_matriz_de_abonos(self):
        # (descripción, valor_venta, abono enviado, ¿válido?, abono limpio)
        casos = [
            ('abono menor', 10_000, 4_000, True, 4_000),
            ('abono igual', 10_000, 10_000, True, 10_000),
            ('abono mayor', 10_000, 10_001, False, None),
            ('abono vacío', 10_000, '', True, 0),
            ('abono 0', 10_000, 0, True, 0),
            # Hoy no se rechaza: la validación solo actúa si el total es mayor que 0.
            ('valor 0 con abono', 0, 5_000, True, 5_000),
        ]
        for descripcion, valor_venta, abono, valido, limpio in casos:
            with self.subTest(descripcion):
                form = self.formulario(valor_venta, abono)
                self.assertEqual(form.is_valid(), valido, form.errors)
                if valido:
                    self.assertEqual(form.cleaned_data['abono_inicial'], limpio)
                else:
                    self.assertEqual(form.errors['abono_inicial'], [self.MENSAJE])

    def test_valor_venta_invalido_deja_pasar_cualquier_abono(self):
        # Si valor_venta no supera su propia validación, no llega a cleaned_data, el total se
        # toma como 0 y el abono no se compara. El formulario es inválido igual por valor_venta.
        form = self.formulario(-1, 999_999)

        self.assertFalse(form.is_valid())
        self.assertIn('valor_venta', form.errors)
        self.assertNotIn('abono_inicial', form.errors)

    def test_abono_negativo_se_rechaza(self):
        form = self.formulario(10_000, -1)

        self.assertFalse(form.is_valid())
        self.assertIn('abono_inicial', form.errors)


# ---------------------------------------------------------------------------
# Tarea 5 · Panel financiero con oráculo ingenuo (decisión D2)
# ---------------------------------------------------------------------------
class ConjuntoConocidoMixin:
    """Doce pedidos con estados, valores, pagos y fechas distintas, y el cálculo ingenuo."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = crear_usuario()
        ana, beto, carla, dario = (crear_cliente() for _ in range(4))
        d = momento_chile
        f = lambda m, dia: d(2026, m, dia).date()  # noqa: E731  fecha de entrega
        # (cliente, estado, valor_venta, fecha_solicitud, fecha_entrega, [(monto, fecha_pago)])
        especificacion = [
            (ana, 'PENDIENTE', 20_000, d(2026, 10, 5), f(10, 20), []),
            (ana, 'EN_PROCESO', 35_000, d(2026, 10, 8), f(10, 18), []),
            (ana, 'EN_PROCESO', 12_000, d(2026, 10, 10), f(10, 12), [(5_000, d(2026, 10, 10))]),
            (beto, 'TERMINADO', 50_000, d(2026, 10, 2), f(10, 9), [(20_000, d(2026, 10, 2))]),
            (beto, 'TERMINADO', 18_000, d(2026, 9, 10), f(9, 25),
             [(9_000, d(2026, 9, 10)), (9_000, d(2026, 10, 3))]),
            (beto, 'ENTREGADO', 40_000, d(2026, 9, 5), f(9, 20), [(40_000, d(2026, 9, 20))]),
            (carla, 'ENTREGADO', 25_000, d(2026, 8, 20), f(9, 1), [(10_000, d(2026, 8, 20))]),
            (carla, 'TERMINADO', 30_000, d(2026, 8, 15), f(8, 30), []),
            # Sobrepago (PENDIENTE_CLIENTE): saldo negativo.
            (carla, 'EN_PROCESO', 15_000, d(2026, 10, 12), f(10, 25),
             [(10_000, d(2026, 10, 12)), (7_000, d(2026, 10, 14))]),
            (dario, 'PENDIENTE', 8_000, d(2026, 3, 3), None, []),
            (dario, 'TERMINADO', 60_000, d(2025, 12, 10), f(12, 20).replace(year=2025),
             [(60_000, d(2025, 12, 20))]),
            (ana, 'PENDIENTE', 45_000, d(2026, 9, 28), f(10, 16), [(15_000, d(2026, 9, 28))]),
        ]
        cls.pedidos = []
        for cliente, estado, valor, solicitud, entrega, pagos in especificacion:
            pedido = crear_pedido(cliente=cliente, estado=estado, valor_venta=valor,
                                  fecha_solicitud=solicitud, fecha_entrega=entrega)
            for monto, fecha in pagos:
                crear_pago(pedido, monto=monto, fecha=fecha)
            cls.pedidos.append(pedido)

    def setUp(self):
        self.client.force_login(self.usuario)
        # dashboard lista los .sql de BASE_DIR/backups (fecha del último respaldo). Se apunta a
        # una carpeta temporal vacía para no depender de los archivos del equipo.
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        parche = mock.patch.object(views.settings, 'BASE_DIR', carpeta.name)
        parche.start()
        self.addCleanup(parche.stop)

    def get(self, ruta):
        with congelar_hora():
            respuesta = self.client.get(ruta)
        self.assertEqual(respuesta.status_code, 200)
        return respuesta.context

    # --- utilidades del oráculo (bucles en Python sobre los objetos) ---
    @staticmethod
    def filas():
        filas = []
        for pedido in Pedido.objects.all():
            pagado = sum(p.monto for p in pedido.pagos.all())
            filas.append({'pedido': pedido, 'pagado': pagado, 'saldo': pedido.valor_venta - pagado,
                          'local': timezone.localtime(pedido.fecha_solicitud)})
        return filas

    @staticmethod
    def hoy():
        return timezone.localtime(AHORA).date()


class EstadisticasPagosOraculoTests(ConjuntoConocidoMixin, TestCase):
    def oraculo(self):
        filas = self.filas()
        terminado_deuda = [f for f in filas if f['pedido'].estado == 'TERMINADO' and f['saldo'] > 0]
        riesgo = [f for f in filas if f['pedido'].estado == 'EN_PROCESO' and f['pagado'] == 0]
        activos = [f for f in filas if f['pedido'].estado != 'ENTREGADO']
        pagados = sum(1 for f in activos if f['saldo'] <= 0)
        sin_abono = sum(1 for f in activos if f['pagado'] == 0)
        pct_pagados = int(pagados / len(activos) * 100)
        pct_sin_abono = int(sin_abono / len(activos) * 100)
        hoy = self.hoy()
        ingresos = 0
        for pedido in Pedido.objects.all():
            for pago in pedido.pagos.all():
                local = timezone.localtime(pago.fecha).date()
                if (local.year, local.month) == (hoy.year, hoy.month):
                    ingresos += pago.monto
        return {
            'deuda_critica_total': sum(f['saldo'] for f in terminado_deuda),
            'deuda_critica_cantidad': len(terminado_deuda),
            'riesgo_total_monto': sum(f['pedido'].valor_venta for f in riesgo),
            'riesgo_cantidad': len(riesgo),
            'proyeccion_total': sum(f['saldo'] for f in filas if f['saldo'] > 0),
            'ingresos_mes_actual': ingresos,
            'pct_pagados': pct_pagados,
            'count_pagados': pagados,
            'pct_sin_abono': pct_sin_abono,
            'count_sin_abono': sin_abono,
            'count_parcial': len(activos) - pagados - sin_abono,
            'pct_parcial': max(0, 100 - pct_pagados - pct_sin_abono),
            'deudores': sorted((f['pedido'] for f in terminado_deuda), key=lambda p: p.fecha_entrega),
        }

    def test_cifras_coinciden_con_el_calculo_ingenuo(self):
        esperado = self.oraculo()
        contexto = self.get('/pagos/estadisticas/')

        for clave, valor in esperado.items():
            if clave == 'deudores':
                continue
            with self.subTest(clave):
                self.assertEqual(contexto[clave], valor)
        self.assertEqual(list(contexto['deudores_list']), esperado['deudores'])

    def test_cifras_fijadas_del_conjunto(self):
        # Valores absolutos del conjunto conocido, para que un error compartido por el
        # oráculo y la vista no pase inadvertido.
        contexto = self.get('/pagos/estadisticas/')
        fijado = {
            'deuda_critica_total': 30_000 + 30_000, 'deuda_critica_cantidad': 2,
            'riesgo_total_monto': 35_000, 'riesgo_cantidad': 1,
            'proyeccion_total': 20_000 + 35_000 + 7_000 + 30_000 + 15_000 + 30_000 + 8_000 + 30_000,
            'ingresos_mes_actual': 5_000 + 20_000 + 9_000 + 10_000 + 7_000,
            'count_pagados': 3, 'count_sin_abono': 4, 'count_parcial': 3,
            'pct_pagados': 30, 'pct_sin_abono': 40, 'pct_parcial': 30,
        }
        for clave, valor in fijado.items():
            with self.subTest(clave):
                self.assertEqual(contexto[clave], valor)

    def test_pedido_de_valor_cero_cuenta_como_pagado_y_sin_abono(self):
        # PENDIENTE_CLIENTE (pedido de $0). Hallazgo propuesto: un pedido activo de $0 sin
        # pagos entra a la vez en «pagados» (saldo 0) y en «sin abono» (pagado 0), y el
        # remanente «parcial» baja en uno.
        antes = self.get('/pagos/estadisticas/')
        crear_pedido(estado='PENDIENTE', valor_venta=0, fecha_solicitud=momento_chile(2026, 10, 6))

        despues = self.get('/pagos/estadisticas/')

        self.assertEqual(despues['count_pagados'], antes['count_pagados'] + 1)
        self.assertEqual(despues['count_sin_abono'], antes['count_sin_abono'] + 1)
        self.assertEqual(despues['count_parcial'], antes['count_parcial'] - 1)


class DashboardOraculoTests(ConjuntoConocidoMixin, TestCase):
    def oraculo(self):
        hoy = self.hoy()
        limite = hoy + timedelta(days=7)
        filas = self.filas()
        no_terminados = [f['pedido'] for f in filas if f['pedido'].estado != 'TERMINADO']
        del_mes = [f['pedido'] for f in filas
                   if (f['local'].year, f['local'].month) == (hoy.year, hoy.month)]
        total = len(del_mes)
        cuenta = Counter(p.estado for p in del_mes)
        por_cliente = Counter(f['pedido'].cliente_id for f in filas)
        return {
            # Criterio actual: «no TERMINADO» incluye ENTREGADO (PENDIENTE_CLIENTE, AUD-02-013).
            'criticos_count': sum(1 for p in no_terminados if p.fecha_entrega and p.fecha_entrega < hoy),
            'urgentes_count': sum(1 for p in no_terminados
                                  if p.fecha_entrega and hoy <= p.fecha_entrega <= limite),
            'pedidos_mes_count': total,
            'total_pedidos': total,
            'pendientes': cuenta['PENDIENTE'],
            'en_proceso': cuenta['EN_PROCESO'],
            'completados': cuenta['TERMINADO'],
            'pct_pendientes': round(cuenta['PENDIENTE'] / total * 100),
            'pct_proceso': round(cuenta['EN_PROCESO'] / total * 100),
            'pct_completados': round(cuenta['TERMINADO'] / total * 100),
            'max_pedidos': max(por_cliente.values()),
            'top': sorted(por_cliente.values(), reverse=True)[:5],
        }

    def test_cifras_coinciden_con_el_calculo_ingenuo(self):
        esperado = self.oraculo()
        contexto = self.get('/')

        for clave, valor in esperado.items():
            if clave == 'top':
                continue
            with self.subTest(clave):
                self.assertEqual(contexto[clave], valor)
        self.assertEqual([c.num_pedidos for c in contexto['top_clientes']], esperado['top'])

    def test_cifras_fijadas_del_conjunto(self):
        contexto = self.get('/')
        fijado = {'criticos_count': 3, 'urgentes_count': 3, 'total_pedidos': 5,
                  'pendientes': 1, 'en_proceso': 3, 'completados': 1, 'max_pedidos': 4}
        for clave, valor in fijado.items():
            with self.subTest(clave):
                self.assertEqual(contexto[clave], valor)

    def test_la_hora_congelada_llega_a_la_vista(self):
        # Si el parche no alcanzara a la vista, todas las cifras dependerían del reloj real.
        self.assertEqual(self.get('/')['fecha_actual'], AHORA)

    def test_registra_metricas_diarias_una_vez(self):
        # Efecto aceptado (AUD-01-006): la lectura del panel escribe en HistorialBD.
        self.get('/')
        self.assertEqual(HistorialBD.objects.count(), 1)


class EstadisticasPedidosOraculoTests(ConjuntoConocidoMixin, TestCase):
    def oraculo(self):
        hoy = self.hoy()
        anterior = (hoy.year, hoy.month - 1) if hoy.month > 1 else (hoy.year - 1, 12)
        filas = self.filas()
        mes = [f['pedido'] for f in filas if (f['local'].year, f['local'].month) == (hoy.year, hoy.month)]
        previo = sum(1 for f in filas if (f['local'].year, f['local'].month) == anterior)
        terminados = sum(1 for p in mes if p.estado == 'TERMINADO')
        por_mes = Counter(f['local'].month for f in filas if f['local'].year == hoy.year)
        valores = [por_mes.get(m, 0) for m in range(1, 13)]
        return {
            'total_mes_actual': len(mes),
            'crecimiento_pct': round((len(mes) - previo) / previo * 100, 1),
            'eficiencia_pct': round(terminados / len(mes) * 100, 1),
            'year_actual': str(hoy.year),
            'valores': valores,
            'max_y_label': int(max(valores) * 1.2),
        }

    def test_cifras_coinciden_con_el_calculo_ingenuo(self):
        esperado = self.oraculo()
        contexto = self.get('/pedidos/estadisticas/')

        for clave, valor in esperado.items():
            if clave == 'valores':
                continue
            with self.subTest(clave):
                self.assertEqual(contexto[clave], valor)
        self.assertEqual([p['valor'] for p in contexto['lista_puntos']], esperado['valores'])

    def test_cifras_fijadas_del_conjunto(self):
        contexto = self.get('/pedidos/estadisticas/')

        self.assertEqual(contexto['total_mes_actual'], 5)
        self.assertEqual(contexto['crecimiento_pct'], 66.7)  # 5 frente a 3 en septiembre
        self.assertEqual(contexto['eficiencia_pct'], 20.0)
        self.assertEqual([p['valor'] for p in contexto['lista_puntos']],
                         [0, 0, 1, 0, 0, 0, 0, 2, 3, 5, 0, 0])
