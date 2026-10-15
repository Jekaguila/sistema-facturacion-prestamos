"""Utilidades para trabajar con dinero.

Regla del proyecto: el dinero SIEMPRE se maneja con ``Decimal`` (nunca con ``float``),
porque ``0.1 + 0.2`` en float da ``0.30000000000000004`` y esos errores se acumulan
en préstamos de muchas cuotas.
"""

from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal("0.01")


def dinero(valor) -> Decimal:
    """Convierte ``valor`` a Decimal con 2 decimales (redondeo comercial)."""
    return Decimal(str(valor)).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def fmt(valor) -> str:
    """Formatea como moneda: ``1234.5`` -> ``$1,234.50``."""
    return f"${dinero(valor):,.2f}"
