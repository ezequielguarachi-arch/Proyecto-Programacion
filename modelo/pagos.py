"""
Jerarquía polimórfica de métodos de pago para Sabor Valluno.
Regla 7: Efectivo (calcula cambio), QR (código de 10 dígitos) y Tarjeta (3% comisión).
"""

from abc import ABC, abstractmethod
import config


class MetodoPago(ABC):
    """Clase abstracta base para los métodos de pago."""

    @abstractmethod
    def calcular_total_con_recargo(self, monto_base: float) -> float:
        """Retorna el monto final a cobrar según posibles comisiones del método."""

    @abstractmethod
    def procesar_pago(self, monto_base: float) -> dict:
        """Valida y procesa el pago, retornando el detalle del comprobante."""

    @abstractmethod
    def nombre_metodo(self) -> str:
        """Nombre legible del método de pago."""


class PagoEfectivo(MetodoPago):
    """Pago en efectivo: valida que el monto recibido cubra el total y calcula el cambio."""

    def __init__(self, monto_recibido: float):
        if monto_recibido <= 0:
            raise ValueError("El monto recibido en efectivo debe ser mayor que cero.")
        self._monto_recibido = round(float(monto_recibido), 2)

    @property
    def monto_recibido(self) -> float:
        return self._monto_recibido

    def nombre_metodo(self) -> str:
        return "Efectivo"

    def calcular_total_con_recargo(self, monto_base: float) -> float:
        return round(float(monto_base), 2)

    def calcular_cambio(self, monto_base: float) -> float:
        total = self.calcular_total_con_recargo(monto_base)
        if self._monto_recibido < total:
            raise ValueError("Monto recibido insuficiente.")
        return round(self._monto_recibido - total, 2)

    def procesar_pago(self, monto_base: float) -> dict:
        total = self.calcular_total_con_recargo(monto_base)
        if self._monto_recibido < total:
            raise ValueError(
                f"Monto recibido insuficiente (Bs {self._monto_recibido:.2f}) "
                f"para cubrir el total (Bs {total:.2f})."
            )
        cambio = round(self._monto_recibido - total, 2)
        return {
            "metodo": self.nombre_metodo(),
            "monto_base": round(monto_base, 2),
            "recargo": 0.00,
            "total_pagado": total,
            "monto_recibido": self._monto_recibido,
            "cambio": cambio,
        }


class PagoQR(MetodoPago):
    """Pago por transferencia QR: requiere un código de transacción de exactamente 10 dígitos."""

    def __init__(self, codigo_transaccion: str):
        codigo = str(codigo_transaccion).strip()
        if not codigo.isdigit() or len(codigo) != config.LONGITUD_CODIGO_QR:
            raise ValueError(
                f"El código de transacción QR debe tener exactamente {config.LONGITUD_CODIGO_QR} dígitos."
            )
        self._codigo_transaccion = codigo

    @property
    def codigo_transaccion(self) -> str:
        return self._codigo_transaccion

    def nombre_metodo(self) -> str:
        return "QR"

    def calcular_total_con_recargo(self, monto_base: float) -> float:
        return round(float(monto_base), 2)

    def procesar_pago(self, monto_base: float) -> dict:
        total = self.calcular_total_con_recargo(monto_base)
        return {
            "metodo": self.nombre_metodo(),
            "monto_base": round(monto_base, 2),
            "recargo": 0.00,
            "total_pagado": total,
            "codigo_transaccion": self._codigo_transaccion,
        }


class PagoTarjeta(MetodoPago):
    """Pago con tarjeta: aplica una comisión del 3% a cargo del cliente."""

    def __init__(self, ultimos_digitos: str = "0000"):
        digitos = str(ultimos_digitos).strip()
        if not digitos.isdigit() or len(digitos) != 4:
            raise ValueError("Debe indicar los últimos 4 dígitos de la tarjeta.")
        self._ultimos_digitos = digitos

    @property
    def ultimos_digitos(self) -> str:
        return self._ultimos_digitos

    def nombre_metodo(self) -> str:
        return "Tarjeta"

    def calcular_total_con_recargo(self, monto_base: float) -> float:
        return round(float(monto_base) * (1 + config.COMISION_TARJETA), 2)

    def procesar_pago(self, monto_base: float) -> dict:
        base = round(float(monto_base), 2)
        total = self.calcular_total_con_recargo(base)
        recargo = round(total - base, 2)
        return {
            "metodo": self.nombre_metodo(),
            "monto_base": base,
            "recargo": recargo,
            "total_pagado": total,
            "tarjeta": f"**** {self._ultimos_digitos}",
        }