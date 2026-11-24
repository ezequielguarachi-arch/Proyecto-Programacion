"""
Configuración de reglas de negocio para el sistema de pedidos Sabor Valluno.
Variante asignada: A
"""

VARIANTE = "A"

# Regla 2: Bebidas (Jarra cuesta 3 veces el vaso)
MULTIPLICADOR_JARRA = 3.0

# Regla 3 (Variante A): Descuento del combo (10%)
DESCUENTO_COMBO = 0.10
MIN_PRODUCTOS_COMBO = 2

# Regla 4 (Variante A): Disponibilidad especial
DIAS_SEMANA = (
    "lunes",
    "martes",
    "miercoles",
    "jueves",
    "viernes",
    "sabado",
    "domingo",
)
DIAS_CHICHARRON = ("domingo",)

# Regla 5 (Variante A): Cargos según tipo de pedido
# Local
MESA_MIN = 1
MESA_MAX = 15

# Para llevar
COSTO_ENVASE_POR_PLATO = 2.00

# Delivery
TARIFAS_DELIVERY = {
    "Cercado": 8.00,
    "Quillacollo": 15.00,
    "Sacaba": 15.00,
    "Vinto": 20.00,
}
SUBTOTAL_ENVIO_GRATIS = 150.00
ZONAS_ENVIO_GRATIS = ("Cercado",)
PEDIDO_MINIMO_DELIVERY = 40.00

# Regla 6: Estados y transiciones válidas
ESTADO_REGISTRADO = "REGISTRADO"
ESTADO_EN_PREPARACION = "EN_PREPARACION"
ESTADO_LISTO = "LISTO"
ESTADO_ENTREGADO = "ENTREGADO"
ESTADO_CANCELADO = "CANCELADO"

TRANSICIONES_VALIDAS = {
    ESTADO_REGISTRADO: (ESTADO_EN_PREPARACION, ESTADO_CANCELADO),
    ESTADO_EN_PREPARACION: (ESTADO_LISTO,),
    ESTADO_LISTO: (ESTADO_ENTREGADO,),
    ESTADO_ENTREGADO: (),
    ESTADO_CANCELADO: (),
}

# Regla 7: Pagos
COMISION_TARJETA = 0.03
LONGITUD_CODIGO_QR = 10

# Regla 8: Validaciones
CANTIDAD_MIN_ITEM = 1
CANTIDAD_MAX_ITEM = 20
LONGITUD_TELEFONO = 8
PREFIJOS_TELEFONO_VALIDOS = ("6", "7")

# Regla 9 (Consultada al docente): Retraso en delivery
MINUTOS_TOLERANCIA_DELIVERY = 60
PORCENTAJE_COMPENSACION_RETRASO = 1.00  # 100% devolución del costo de envío