"""
Jerarquía polimórfica de pedidos para Sabor Valluno (Variante A).
Alineado 1:1 con el diagrama de clases: ItemPedido, Pedido, PedidoLocal, PedidoLlevar y PedidoDelivery.
"""

from abc import ABC, abstractmethod
import config
from modelo.productos import Producto
from modelo.clientes import Cliente
from modelo.pagos import MetodoPago


class ItemPedido:
    """Representa una línea de detalle dentro de un pedido (Producto + cantidad)."""

    def __init__(self, producto: Producto, cantidad: int = 1):
        if not isinstance(producto, Producto):
            raise TypeError("El ítem debe contener una instancia válida de Producto.")
        self._producto = producto
        self.cantidad = cantidad

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise ValueError("La cantidad debe ser un número entero.")
        if not (config.CANTIDAD_MIN_ITEM <= valor <= config.CANTIDAD_MAX_ITEM):
            raise ValueError(
                f"La cantidad debe estar entre {config.CANTIDAD_MIN_ITEM} y {config.CANTIDAD_MAX_ITEM}."
            )
        self._cantidad = valor

    def calcular_importe(self) -> float:
        """Calcula el importe total de esta línea (precio unitario * cantidad)."""
        return round(self._producto.calcular_precio() * self._cantidad, 2)

    def total_platos(self) -> int:
        return self._producto.contar_platos() * self._cantidad

    def __str__(self) -> str:
        return (
            f"{self._cantidad}x {self._producto.nombre} "
            f"(Bs {self._producto.calcular_precio():.2f} c/u) = Bs {self.calcular_importe():.2f}"
        )


class Pedido(ABC):
    """Clase abstracta base para cualquier modalidad de pedido."""

    _contador_numero = 1

    def __init__(self, cliente: Cliente, dia: str):
        if not isinstance(cliente, Cliente):
            raise TypeError("El pedido requiere un Cliente válido.")
        dia_norm = str(dia).strip().lower()
        if dia_norm not in config.DIAS_SEMANA:
            raise ValueError(f"Día inválido '{dia}'. Debe ser uno de: {', '.join(config.DIAS_SEMANA)}.")

        self._numero = Pedido._contador_numero
        Pedido._contador_numero += 1
        self._cliente = cliente
        self._dia = dia_norm
        self._items: list[ItemPedido] = []
        self._estado = config.ESTADO_REGISTRADO
        self._comprobante_pago: dict | None = None

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def dia(self) -> str:
        return self._dia

    @property
    def items(self) -> tuple[ItemPedido, ...]:
        return tuple(self._items)

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def comprobante_pago(self) -> dict | None:
        return self._comprobante_pago

    def _verificar_editable(self) -> None:
        if self._estado != config.ESTADO_REGISTRADO:
            raise RuntimeError(
                f"No se puede modificar el pedido #{self._numero} porque está en estado '{self._estado}'."
            )

    def agregar_producto(self, producto: Producto, cantidad: int = 1) -> None:
        self._verificar_editable()
        if not producto.esta_disponible(self._dia):
            raise ValueError(
                f"El producto '{producto.nombre}' no está disponible los días {self._dia}."
            )
        for item in self._items:
            if item.producto is producto:
                item.cantidad = item.cantidad + cantidad
                return
        self._items.append(ItemPedido(producto, cantidad))

    def quitar_producto(self, indice: int) -> None:
        self._verificar_editable()
        if not (0 <= indice < len(self._items)):
            raise IndexError("Índice de ítem fuera de rango.")
        self._items.pop(indice)

    def cancelar_pedido(self) -> None:
        """Cancela el pedido si aún se encuentra en estado REGISTRADO."""
        self.cambiar_estado(config.ESTADO_CANCELADO)

    def calcular_subtotal(self) -> float:
        return round(sum(item.calcular_importe() for item in self._items), 2)

    def contar_total_platos(self) -> int:
        return sum(item.total_platos() for item in self._items)

    @abstractmethod
    def calcular_cargo(self) -> float:
        """Retorna el cargo adicional según la modalidad (mesa, envases o delivery)."""

    @abstractmethod
    def tipo_pedido(self) -> str:
        """Retorna la descripción de la modalidad del pedido."""

    def calcular_total(self) -> float:
        if not self._items:
            raise ValueError("El pedido no tiene productos registrados.")
        return round(self.calcular_subtotal() + self.calcular_cargo(), 2)

    def cambiar_estado(self, nuevo_estado: str) -> None:
        estado_norm = str(nuevo_estado).strip().upper()
        permitidos = config.TRANSICIONES_VALIDAS.get(self._estado, ())
        if estado_norm not in permitidos:
            raise ValueError(
                f"Transición inválida de '{self._estado}' a '{estado_norm}'. "
                f"Permitidas: {permitidos if permitidos else 'Ninguna (estado final)'}."
            )
        self._estado = estado_norm

    def pagar(self, metodo_pago: MetodoPago) -> dict:
        if self._estado == config.ESTADO_CANCELADO:
            raise RuntimeError("No se puede cobrar un pedido cancelado.")
        if self._comprobante_pago is not None:
            raise RuntimeError("Este pedido ya fue pagado.")
        total = self.calcular_total()
        self._comprobante_pago = metodo_pago.procesar_pago(total)
        return self._comprobante_pago

    def generar_resumen(self) -> str:
        lineas = [
            f"=== PEDIDO #{self._numero} [{self.tipo_pedido()}] ===",
            f"Cliente: {self._cliente}",
            f"Día: {self._dia.capitalize()} | Estado: {self._estado}",
            "Detalle:",
        ]
        for item in self._items:
            lineas.append(f"  - {item}")
        lineas.append(f"Subtotal: Bs {self.calcular_subtotal():.2f}")
        lineas.append(f"Cargo modalidad: Bs {self.calcular_cargo():.2f}")
        lineas.append(f"TOTAL: Bs {self.calcular_total():.2f}")
        if self._comprobante_pago:
            pago = self._comprobante_pago
            lineas.append(
                f"Pago ({pago['metodo']}): Total cobrado Bs {pago['total_pagado']:.2f}"
            )
        return "\n".join(lineas)


class PedidoLocal(Pedido):
    """Pedido para consumo en salón (mesas 1 a 15, sin recargo)."""

    def __init__(self, cliente: Cliente, dia: str, mesa: int):
        super().__init__(cliente, dia)
        self.mesa = mesa

    @property
    def mesa(self) -> int:
        return self._mesa

    @mesa.setter
    def mesa(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise ValueError("El número de mesa debe ser un entero.")
        if not (config.MESA_MIN <= valor <= config.MESA_MAX):
            raise ValueError(
                f"Número de mesa inválido ({valor}). Debe estar entre {config.MESA_MIN} y {config.MESA_MAX}."
            )
        self._mesa = valor

    def tipo_pedido(self) -> str:
        return f"Local - Mesa {self._mesa}"

    def calcular_cargo(self) -> float:
        return 0.00


class PedidoLlevar(Pedido):
    """Pedido para llevar: cobra Bs 2.00 por cada envase (1 envase por plato)."""

    @property
    def cantidad_envases(self) -> int:
        return self.contar_total_platos()

    def tipo_pedido(self) -> str:
        return f"Para Llevar ({self.cantidad_envases} envases)"

    def calcular_cargo(self) -> float:
        return round(self.cantidad_envases * config.COSTO_ENVASE_POR_PLATO, 2)


class PedidoDelivery(Pedido):
    """Pedido con entrega a domicilio (Variante A + Regla 9 de retraso)."""

    def __init__(self, cliente: Cliente, dia: str, zona: str):
        if not cliente.direccion:
            raise ValueError("Para pedidos delivery, el cliente debe tener una dirección registrada.")
        zona_norm = str(zona).strip().title()
        if zona_norm not in config.TARIFAS_DELIVERY:
            raise ValueError(
                f"Zona de delivery no cubierta '{zona}'. "
                f"Zonas válidas: {', '.join(config.TARIFAS_DELIVERY.keys())}."
            )
        super().__init__(cliente, dia)
        self._zona = zona_norm
        self._minutos_entrega: int | None = None

    @property
    def zona(self) -> str:
        return self._zona

    @property
    def minutos_entrega(self) -> int | None:
        return self._minutos_entrega

    def tipo_pedido(self) -> str:
        return f"Delivery - Zona {self._zona}"

    def registrar_entrega(self, minutos_demora: int) -> None:
        """Regla 9: Registra el tiempo real de entrega para evaluar compensación por retraso."""
        if minutos_demora <= 0:
            raise ValueError("Los minutos de entrega deben ser mayores a cero.")
        self._minutos_entrega = int(minutos_demora)
        if self._estado == config.ESTADO_LISTO:
            self.cambiar_estado(config.ESTADO_ENTREGADO)

    def tuvo_retraso(self) -> bool:
        return (
            self._minutos_entrega is not None
            and self._minutos_entrega > config.MINUTOS_TOLERANCIA_DELIVERY
        )

    def calcular_cargo(self) -> float:
        subtotal = self.calcular_subtotal()
        if subtotal < config.PEDIDO_MINIMO_DELIVERY:
            raise ValueError(
                f"El subtotal (Bs {subtotal:.2f}) no alcanza el mínimo de "
                f"Bs {config.PEDIDO_MINIMO_DELIVERY:.2f} para delivery."
            )
        if (
            self._zona in config.ZONAS_ENVIO_GRATIS
            and subtotal >= config.SUBTOTAL_ENVIO_GRATIS
        ):
            costo_envio = 0.00
        else:
            costo_envio = config.TARIFAS_DELIVERY[self._zona]

        if self.tuvo_retraso():
            descuento_retraso = costo_envio * config.PORCENTAJE_COMPENSACION_RETRASO
            return round(costo_envio - descuento_retraso, 2)

        return round(costo_envio, 2)