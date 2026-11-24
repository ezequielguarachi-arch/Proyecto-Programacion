"""
Jerarquía de productos del sistema Sabor Valluno (Patrón Composite).
Variante A: Descuento de combo del 10%, chicharrón solo los domingos.
"""

from abc import ABC, abstractmethod
import config


class Producto(ABC):
    """Clase abstracta base para todos los elementos del menú."""

    def __init__(self, nombre: str, precio: float):
        self.nombre = nombre
        self.precio = precio

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("El precio debe ser mayor que cero.")
        self._precio = round(float(valor), 2)

    @abstractmethod
    def calcular_precio(self) -> float:
        """Retorna el precio final unitario del producto."""

    @abstractmethod
    def esta_disponible(self, dia: str) -> bool:
        """Indica si el producto se vende el día indicado."""

    @abstractmethod
    def contar_platos(self) -> int:
        """Retorna cuántos platos contiene (para cálculo de envases)."""

    def contiene(self, objetivo: "Producto") -> bool:
        """Verifica si este producto es igual a objetivo (evita ciclos en combos)."""
        return self is objetivo

    def __str__(self) -> str:
        return f"{self.nombre} - Bs {self.calcular_precio():.2f}"


class Plato(Producto):
    """Representa un plato de comida típica (silpancho, pique macho, chicharrón, etc.)."""

    def __init__(self, nombre: str, precio: float, dias: list[str] | tuple[str, ...] | None = None):
        super().__init__(nombre, precio)
        if dias is None or len(dias) == 0:
            self.__dias = tuple(config.DIAS_SEMANA)
        else:
            self.__dias = tuple(d.strip().lower() for d in dias)

    @property
    def dias(self) -> tuple[str, ...]:
        return self.__dias

    def calcular_precio(self) -> float:
        return self._precio

    def esta_disponible(self, dia: str) -> bool:
        return dia.strip().lower() in self.__dias

    def contar_platos(self) -> int:
        return 1


class Bebida(Producto):
    """Representa una bebida en vaso o jarra (jarra = 3x precio del vaso)."""

    def __init__(self, nombre: str, precio_vaso: float, es_jarra: bool = False):
        super().__init__(nombre, precio_vaso)
        self.__es_jarra = bool(es_jarra)

    @property
    def es_jarra(self) -> bool:
        return self.__es_jarra

    def calcular_precio(self) -> float:
        if self.__es_jarra:
            return round(self._precio * config.MULTIPLICADOR_JARRA, 2)
        return self._precio

    def esta_disponible(self, dia: str) -> bool:
        return True

    def contar_platos(self) -> int:
        return 0


class Combo(Producto):
    """Agrupación de 2 o más productos (platos, bebidas u otros combos) con descuento."""

    def __init__(
        self,
        nombre: str,
        productos: list[Producto] | None = None,
        descuento: float = config.DESCUENTO_COMBO,
    ):
        super().__init__(nombre, 1.0)
        self.__productos: list[Producto] = []
        self.descuento = descuento
        if productos:
            for prod in productos:
                self.agregar_producto(prod)

    @property
    def productos(self) -> tuple[Producto, ...]:
        return tuple(self.__productos)

    @property
    def descuento(self) -> float:
        return self.__descuento

    @descuento.setter
    def descuento(self, valor: float) -> None:
        if not (0 <= valor < 1):
            raise ValueError("El descuento debe estar entre 0 y 1 (ej. 0.10 para 10%).")
        self.__descuento = float(valor)

    def agregar_producto(self, producto: Producto) -> None:
        if producto.contiene(self):
            raise ValueError("Un combo no puede contenerse a sí mismo (ni directa ni indirectamente).")
        self.__productos.append(producto)
        self._precio = self.calcular_precio() if len(self.__productos) >= 1 else 1.0

    def contiene(self, objetivo: Producto) -> bool:
        if self is objetivo:
            return True
        return any(prod.contiene(objetivo) for prod in self.__productos)

    def _validar_minimo(self) -> None:
        if len(self.__productos) < config.MIN_PRODUCTOS_COMBO:
            raise ValueError(
                f"El combo '{self.nombre}' debe tener al menos {config.MIN_PRODUCTOS_COMBO} productos."
            )

    def calcular_precio(self) -> float:
        self._validar_minimo()
        suma = sum(prod.calcular_precio() for prod in self.__productos)
        return round(suma * (1 - self.__descuento), 2)

    def esta_disponible(self, dia: str) -> bool:
        self._validar_minimo()
        return all(prod.esta_disponible(dia) for prod in self.__productos)

    def contar_platos(self) -> int:
        self._validar_minimo()
        return sum(prod.contar_platos() for prod in self.__productos)