"""
Suite de pruebas unitarias para el sistema Sabor Valluno (Variante A).
Valida todas las reglas de negocio, encapsulación, polimorfismo y manejo de excepciones.
Ejecutar con: python pruebas.py
"""

import unittest
import config
from modelo.productos import Plato, Bebida, Combo
from modelo.clientes import Cliente
from modelo.pedidos import ItemPedido, PedidoLocal, PedidoLlevar, PedidoDelivery
from modelo.pagos import PagoEfectivo, PagoQR, PagoTarjeta
from restaurante import Restaurant


class TestProductosVarianteA(unittest.TestCase):
    """Pruebas de Reglas 1, 2, 3 y 4 (Platos, Bebidas, Combos y Disponibilidad)."""

    def test_precio_plato_y_bebida_vaso_jarra(self):
        silpancho = Plato("Silpancho", 35.00)
        chicha_vaso = Bebida("Chicha", 6.00, es_jarra=False)
        chicha_jarra = Bebida("Chicha", 6.00, es_jarra=True)

        self.assertEqual(silpancho.calcular_precio(), 35.00)
        self.assertEqual(chicha_vaso.calcular_precio(), 6.00)
        self.assertEqual(chicha_jarra.calcular_precio(), 18.00)  # 3x vaso

    def test_combo_simple_y_anidado_descuento_10_porciento(self):
        silpancho = Plato("Silpancho", 35.00)
        pique = Plato("Pique Macho", 55.00)
        vaso = Bebida("Chicha", 6.00, es_jarra=False)
        jarra = Bebida("Chicha", 6.00, es_jarra=True)

        combo1 = Combo("Combo Valluno", [silpancho, vaso])  # (35 + 6) * 0.90 = 36.90
        self.assertEqual(combo1.calcular_precio(), 36.90)
        self.assertEqual(combo1.contar_platos(), 1)

        # Combo anidado que contiene otro combo
        combo_familiar = Combo("Combo Familiar", [pique, combo1, jarra])
        # (55 + 36.90 + 18) * 0.90 = 109.90 * 0.90 = 98.91
        self.assertEqual(combo_familiar.calcular_precio(), 98.91)
        self.assertEqual(combo_familiar.contar_platos(), 2)

    def test_combo_evita_ciclos_y_valida_minimo(self):
        p1 = Plato("Silpancho", 35.00)
        c1 = Combo("Combo A", [p1])
        with self.assertRaises(ValueError):
            c1.calcular_precio()  # Menos de 2 productos

        with self.assertRaises(ValueError):
            c1.agregar_producto(c1)  # Autocontención directa

        p2 = Bebida("Garapiña", 8.00)
        c1.agregar_producto(p2)
        c2 = Combo("Combo B", [c1, p1])
        with self.assertRaises(ValueError):
            c1.agregar_producto(c2)  # Ciclo indirecto

    def test_disponibilidad_chicharron_solo_domingo(self):
        chicharron = Plato("Chicharrón", 50.00, dias=["domingo"])
        vaso = Bebida("Chicha", 6.00)
        combo_dom = Combo("Combo Dominical", [chicharron, vaso])

        self.assertTrue(chicharron.esta_disponible("domingo"))
        self.assertFalse(chicharron.esta_disponible("martes"))
        self.assertTrue(combo_dom.esta_disponible("domingo"))
        self.assertFalse(combo_dom.esta_disponible("viernes"))

    def test_encapsulacion_precio_invalido(self):
        with self.assertRaises(ValueError):
            Plato("Plato Inválido", -10.0)


class TestPedidosYReglasNegocio(unittest.TestCase):
    """Pruebas de Reglas 5, 6, 8 y 9 (Modalidades, Estados, Validaciones y Retraso)."""

    def setUp(self):
        self.cliente = Cliente("Ana López", "71234567", "Calle España 123, Cercado")
        self.silpancho = Plato("Silpancho", 35.00)
        self.pique = Plato("Pique Macho", 55.00)
        self.chicharron = Plato("Chicharrón", 50.00, dias=["domingo"])
        self.vaso = Bebida("Chicha", 6.00)

    def test_validacion_telefono_cliente(self):
        with self.assertRaises(ValueError):
            Cliente("Pedro", "41234567")  # No empieza en 6 o 7
        with self.assertRaises(ValueError):
            Cliente("Pedro", "712345")  # Menos de 8 dígitos

    def test_pedido_local_mesas_y_cargo_cero(self):
        pedido = PedidoLocal(self.cliente, "lunes", mesa=10)
        pedido.agregar_producto(self.silpancho, 2)
        self.assertEqual(pedido.calcular_cargo(), 0.00)
        self.assertEqual(pedido.calcular_total(), 70.00)

        with self.assertRaises(ValueError):
            PedidoLocal(self.cliente, "lunes", mesa=16)  # Mesa fuera de rango 1..15

    def test_pedido_para_llevar_envases_incluyendo_combos(self):
        combo = Combo("Combo Dúo", [self.silpancho, self.pique, self.vaso])  # 2 platos
        pedido = PedidoLlevar(self.cliente, "martes")
        pedido.agregar_producto(combo, 2)  # 4 platos totales -> 4 * 2.00 = Bs 8.00
        self.assertEqual(pedido.cantidad_envases, 4)
        self.assertEqual(pedido.calcular_cargo(), 8.00)

    def test_pedido_delivery_tarifas_envio_gratis_y_minimo(self):
        # Pedido mínimo Bs 40
        p_bajo = PedidoDelivery(self.cliente, "jueves", "Cercado")
        p_bajo.agregar_producto(self.silpancho, 1)  # Bs 35 < 40
        with self.assertRaises(ValueError):
            p_bajo.calcular_total()

        # Cercado con subtotal < 150 -> Bs 8.00
        p_cercado = PedidoDelivery(self.cliente, "jueves", "Cercado")
        p_cercado.agregar_producto(self.pique, 1)  # Bs 55
        self.assertEqual(p_cercado.calcular_cargo(), 8.00)

        # Cercado con subtotal >= 150 -> Envío gratis (Bs 0.00)
        p_gratis = PedidoDelivery(self.cliente, "jueves", "Cercado")
        p_gratis.agregar_producto(self.pique, 3)  # Bs 165 >= 150
        self.assertEqual(p_gratis.calcular_cargo(), 0.00)

        # Quillacollo / Sacaba -> Bs 15.00; Vinto -> Bs 20.00
        p_vinto = PedidoDelivery(self.cliente, "jueves", "Vinto")
        p_vinto.agregar_producto(self.pique, 3)  # Bs 165 (no aplica envío gratis fuera de Cercado)
        self.assertEqual(p_vinto.calcular_cargo(), 20.00)

    def test_regla_9_compensacion_retraso_delivery(self):
        pedido = PedidoDelivery(self.cliente, "sabado", "Sacaba")
        pedido.agregar_producto(self.pique, 1)  # Subtotal 55, envío normal 15
        self.assertEqual(pedido.calcular_cargo(), 15.00)

        pedido.cambiar_estado(config.ESTADO_EN_PREPARACION)
        pedido.cambiar_estado(config.ESTADO_LISTO)
        pedido.registrar_entrega(minutos_demora=65)  # > 60 min -> 100% descuento en envío

        self.assertTrue(pedido.tuvo_retraso())
        self.assertEqual(pedido.estado, config.ESTADO_ENTREGADO)
        self.assertEqual(pedido.calcular_cargo(), 0.00)
        self.assertEqual(pedido.calcular_total(), 55.00)

    def test_rechazo_producto_no_disponible_en_dia(self):
        pedido = PedidoLocal(self.cliente, "miercoles", mesa=3)
        with self.assertRaises(ValueError):
            pedido.agregar_producto(self.chicharron, 1)

    def test_transiciones_estado_y_bloqueo_edicion(self):
        pedido = PedidoLocal(self.cliente, "viernes", mesa=2)
        pedido.agregar_producto(self.silpancho, 1)

        # Salto inválido de REGISTRADO directo a ENTREGADO
        with self.assertRaises(ValueError):
            pedido.cambiar_estado(config.ESTADO_ENTREGADO)

        pedido.cambiar_estado(config.ESTADO_EN_PREPARACION)
        # No se puede agregar productos fuera de REGISTRADO
        with self.assertRaises(RuntimeError):
            pedido.agregar_producto(self.vaso, 1)


class TestMetodosPagoYRestaurante(unittest.TestCase):
    """Pruebas de Regla 7 (Efectivo, QR, Tarjeta) y clase Restaurant."""

    def test_pagos_polimorficos(self):
        efectivo = PagoEfectivo(100.00)
        res_ef = efectivo.procesar_pago(75.50)
        self.assertEqual(res_ef["cambio"], 24.50)

        with self.assertRaises(ValueError):
            PagoEfectivo(50.00).procesar_pago(75.50)

        qr = PagoQR("9876543210")
        res_qr = qr.procesar_pago(80.00)
        self.assertEqual(res_qr["total_pagado"], 80.00)

        with self.assertRaises(ValueError):
            PagoQR("12345")  # Menos de 10 dígitos

        tarjeta = PagoTarjeta("1234")
        res_tar = tarjeta.procesar_pago(100.00)
        self.assertEqual(res_tar["recargo"], 3.00)
        self.assertEqual(res_tar["total_pagado"], 103.00)

    def test_integracion_restaurant(self):
        rest = Restaurant("Sabor Valluno")
        rest.cargar_menu_base()
        cliente = rest.registrar_cliente(Cliente("Luis Rojas", "67890123"))
        pedido = PedidoLocal(cliente, "domingo", mesa=1)
        pedido.agregar_producto(rest.buscar_producto("Chicharrón de Cerdo"), 2)
        rest.registrar_pedido(pedido)
        rest.cobrar_pedido(pedido.numero, PagoTarjeta("9999"))
        self.assertEqual(rest.calcular_recaudacion_total(), 103.00)


if __name__ == "__main__":
    unittest.main(verbosity=2)