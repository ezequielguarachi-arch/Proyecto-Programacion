"""
Modelo de Cliente para el sistema de pedidos Sabor Valluno.
Regla 8: El teléfono tiene 8 dígitos y empieza en 6 o 7.
"""

import config


class Cliente:
    """Representa un cliente del restaurante."""

    def __init__(self, nombre: str, telefono: str, direccion: str = ""):
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        tel = str(valor).strip()
        if (
            not tel.isdigit()
            or len(tel) != config.LONGITUD_TELEFONO
            or not tel.startswith(config.PREFIJOS_TELEFONO_VALIDOS)
        ):
            raise ValueError(
                f"El teléfono debe tener {config.LONGITUD_TELEFONO} dígitos y empezar en "
                f"{' o '.join(config.PREFIJOS_TELEFONO_VALIDOS)}."
            )
        self._telefono = tel

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        self._direccion = valor.strip() if valor else ""

    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        tel = str(telefono).strip()
        return (
            tel.isdigit()
            and len(tel) == config.LONGITUD_TELEFONO
            and tel.startswith(config.PREFIJOS_TELEFONO_VALIDOS)
        )

    def mostrar_datos(self) -> str:
        return str(self)

    def __str__(self) -> str:
        dir_txt = f" | Dir: {self.direccion}" if self.direccion else ""
        return f"{self.nombre} (Tel: {self.telefono}{dir_txt})"