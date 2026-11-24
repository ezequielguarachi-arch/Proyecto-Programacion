"""
Clase controladora Restaurant para el sistema Sabor Valluno (Variante A).
Alineada con el diagrama de clases: gestiona menú, clientes, pedidos y reportes.
"""

import config
from modelo.productos import Producto, Plato, Bebida, Combo
from modelo.clientes import Cliente
from modelo.pedidos import Pedido, PedidoLocal, PedidoLlevar, PedidoDelivery
from modelo.pagos import MetodoPago


class Restaurant:
    """Gestiona el catálogo del menú, los clientes y los pedidos de Sabor Valluno."""

    def __init__(self, nombre: str = "Sabor Valluno"):
        self._nombre = nombre
        self._menu: list[Producto] = []
        self._clientes: dict[str, Cliente] = {}
        self._pedidos: list[Pedido] = []

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def menu(self) -> tuple[Producto, ...]:
        return tuple(self._menu)

    @property
    def pedidos(self) -> tuple[Pedido, ...]:
        return tuple(self._pedidos)

    # --- Gestión de Menú (según diagrama: registrar_menu y mostrar_menu) ---
    def registrar_menu(self, producto: Producto) -> None:
        """Registra un plato, bebida o combo en el catálogo del restaurante."""
        if not isinstance(producto, Producto):
            raise TypeError("Solo se pueden registrar instancias de Producto en el menú.")
        if any(p.nombre.lower() == producto.nombre.lower() for p in self._menu):
            raise ValueError(f"El producto '{producto.nombre}' ya existe en el menú.")
        self._menu.append(producto)

    def cargar_menu_base(self) -> None:
        """Carga el menú típico cochabambino inicial de Sabor Valluno (Variante A)."""
        silpancho = Plato("Silpancho Cochabambino", 35.00)
        pique = Plato("Pique Macho", 55.00)
        chicharron = Plato("Chicharrón de Cerdo", 50.00, dias=list(config.DIAS_CHICHARRON))
        chicha_vaso = Bebida("Chicha Kullu (Vaso)", 6.00, es_jarra=False)
        chicha_jarra = Bebida("Chicha Kullu (Jarra)", 6.00, es_jarra=True)
        garapina_vaso = Bebida("Garapiña (Vaso)", 8.00, es_jarra=False)

        combo_valluno = Combo("Combo Valluno", [silpancho, chicha_vaso])
        combo_familiar = Combo("Combo Familiar", [pique, combo_valluno, chicha_jarra])

        for item in (
            silpancho,
            pique,
            chicharron,
            chicha_vaso,
            chicha_jarra,
            garapina_vaso,
            combo_valluno,
            combo_familiar,
        ):
            self.registrar_menu(item)

    def buscar_producto(self, nombre: str) -> Producto:
        """Busca un producto en el menú por nombre exacto (sin distinguir mayúsculas)."""
        nombre_norm = nombre.strip().lower()
        for prod in self._menu:
            if prod.nombre.lower() == nombre_norm:
                return prod
        raise LookupError(f"Producto '{nombre}' no encontrado en el menú.")

    def mostrar_menu(self, dia: str | None = None) -> str:
        """Retorna el menú formateado, filtrando por disponibilidad si se indica un día."""
        encabezado = f"=== MENÚ {self._nombre.upper()}"
        if dia:
            encabezado += f" ({dia.strip().upper()})"
        encabezado += " ==="

        lineas = [encabezado]
        for idx, prod in enumerate(self._menu, start=1):
            if dia is None or prod.esta_disponible(dia):
                lineas.append(f"  {idx}. {prod}")
        if len(lineas) == 1:
            lineas.append("  (No hay productos disponibles para este día)")
        return "\n".join(lineas)

    # --- Gestión de Clientes ---
    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        self._clientes[cliente.telefono] = cliente
        return cliente

    def buscar_cliente(self, telefono: str) -> Cliente:
        tel = str(telefono).strip()
        if tel not in self._clientes:
            raise LookupError(f"No existe cliente registrado con teléfono {tel}.")
        return self._clientes[tel]

    # --- Gestión de Pedidos ---
    def registrar_pedido(self, pedido: Pedido) -> Pedido:
        if not isinstance(pedido, Pedido):
            raise TypeError("Debe proporcionar una instancia válida de Pedido.")
        self._pedidos.append(pedido)
        return pedido

    def buscar_pedido(self, numero: int) -> Pedido:
        for pedido in self._pedidos:
            if pedido.numero == numero:
                return pedido
        raise LookupError(f"Pedido #{numero} no encontrado.")

    def cobrar_pedido(self, numero: int, metodo_pago: MetodoPago) -> dict:
        pedido = self.buscar_pedido(numero)
        return pedido.pagar(metodo_pago)

    # --- Reportes operativos ---
    def listar_pedidos_por_estado(self, estado: str) -> list[Pedido]:
        estado_norm = estado.strip().upper()
        return [p for p in self._pedidos if p.estado == estado_norm]

    def calcular_recaudacion_total(self) -> float:
        """Suma el total cobrado (incluyendo comisiones de tarjeta si hubo) de pedidos pagados."""
        total = 0.0
        for pedido in self._pedidos:
            if pedido.comprobante_pago is not None:
                total += pedido.comprobante_pago["total_pagado"]
        return round(total, 2)

    def generar_reporte_general(self) -> str:
        lineas = [
            f"=== REPORTE GENERAL - {self._nombre.upper()} ===",
            f"Total productos en menú: {len(self._menu)}",
            f"Total clientes registrados: {len(self._clientes)}",
            f"Total pedidos registrados: {len(self._pedidos)}",
            f"Recaudación cobrada: Bs {self.calcular_recaudacion_total():.2f}",
        ]
        for estado in config.TRANSICIONES_VALIDAS.keys():
            cantidad = len(self.listar_pedidos_por_estado(estado))
            lineas.append(f"  - {estado}: {cantidad}")
        return "\n".join(lineas)