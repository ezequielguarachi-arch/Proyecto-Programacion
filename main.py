"""
Punto de entrada principal del sistema de pedidos Sabor Valluno (Variante A).
Permite ejecutar una demostración completa o interactuar mediante menú en consola.
"""

import config
from modelo.productos import Plato, Bebida, Combo
from modelo.clientes import Cliente
from modelo.pedidos import PedidoLocal, PedidoLlevar, PedidoDelivery
from modelo.pagos import PagoEfectivo, PagoQR, PagoTarjeta
from restaurante import Restaurant


def ejecutar_demostracion() -> None:
    """Demuestra el flujo completo de Sabor Valluno aplicando todas las reglas de Variante A."""
    restaurante = Restaurant("Sabor Valluno")
    restaurante.cargar_menu_base()

    print(restaurante.mostrar_menu("domingo"))
    print()

    # 1. Pedido Local en Mesa 5 con Combo Valluno + pago en Efectivo
    c1 = restaurante.registrar_cliente(Cliente("Carlos Mamani", "71234567"))
    p1 = PedidoLocal(c1, "miercoles", mesa=5)
    p1.agregar_producto(restaurante.buscar_producto("Combo Valluno"), 2)
    p1.agregar_producto(restaurante.buscar_producto("Garapiña (Vaso)"), 1)
    restaurante.registrar_pedido(p1)
    p1.cambiar_estado(config.ESTADO_EN_PREPARACION)
    p1.cambiar_estado(config.ESTADO_LISTO)
    p1.cambiar_estado(config.ESTADO_ENTREGADO)
    comp1 = restaurante.cobrar_pedido(p1.numero, PagoEfectivo(100.00))
    print(p1.generar_resumen())
    print(f"Cambio entregado: Bs {comp1['cambio']:.2f}\n")

    # 2. Pedido Para Llevar en Domingo (con Chicharrón y Combo Familiar) + pago QR
    c2 = restaurante.registrar_cliente(Cliente("María Quispe", "68901234"))
    p2 = PedidoLlevar(c2, "domingo")
    p2.agregar_producto(restaurante.buscar_producto("Chicharrón de Cerdo"), 1)
    p2.agregar_producto(restaurante.buscar_producto("Combo Familiar"), 1)
    restaurante.registrar_pedido(p2)
    restaurante.cobrar_pedido(p2.numero, PagoQR("1234567890"))
    print(p2.generar_resumen())
    print()

    # 3. Pedido Delivery a Quillacollo con retraso (> 60 min -> envío gratis por Regla 9) + Tarjeta (3%)
    c3 = restaurante.registrar_cliente(
        Cliente("Juan Pérez", "76543210", "Av. Blanco Galindo Km 12, Quillacollo")
    )
    p3 = PedidoDelivery(c3, "viernes", zona="Quillacollo")
    p3.agregar_producto(restaurante.buscar_producto("Pique Macho"), 1)
    restaurante.registrar_pedido(p3)
    p3.cambiar_estado(config.ESTADO_EN_PREPARACION)
    p3.cambiar_estado(config.ESTADO_LISTO)
    p3.registrar_entrega(minutos_demora=75)  # Excede 60 min -> descuento 100% envío
    comp3 = restaurante.cobrar_pedido(p3.numero, PagoTarjeta("4589"))
    print(p3.generar_resumen())
    print(f"Comisión tarjeta (3%): Bs {comp3['recargo']:.2f}\n")

    print(restaurante.generar_reporte_general())


def menu_interactivo() -> None:
    """Interfaz de consola para operar el restaurante."""
    restaurante = Restaurant("Sabor Valluno")
    restaurante.cargar_menu_base()

    while True:
        print("\n--- SISTEMA SABOR VALLUNO (VARIANTE A) ---")
        print("1. Mostrar menú del día")
        print("2. Ejecutar demostración completa (Variante A)")
        print("3. Ver reporte general")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            dia = input("Ingrese el día de la semana (o Enter para ver todo): ").strip()
            print(restaurante.mostrar_menu(dia if dia else None))
        elif opcion == "2":
            ejecutar_demostracion()
        elif opcion == "3":
            print(restaurante.generar_reporte_general())
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    ejecutar_demostracion()