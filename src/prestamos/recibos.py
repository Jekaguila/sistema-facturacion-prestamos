"""Recibos: documento inmutable que prueba un pago.

Responsabilidad única (SRP): esta clase solo ARMA el recibo. No calcula intereses
(eso es de ``Prestamo``), no lo imprime (eso es de ``formatos``) ni lo guarda
(eso es del almacén).
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from .prestamo import Pago, Prestamo


class Numeracion(Protocol):
    """Cualquier objeto con ``siguiente()`` sirve (tipado estructural, PEP 544)."""

    def siguiente(self) -> str: ...


class SecuenciaNumeracion:
    """Genera R-000001, R-000002..."""

    def __init__(self, prefijo: str = "R", inicio: int = 1):
        self._prefijo = prefijo
        self._actual = inicio - 1

    def siguiente(self) -> str:
        self._actual += 1
        return f"{self._prefijo}-{self._actual:06d}"


@dataclass(frozen=True)
class Recibo:
    numero: str
    fecha_emision: date
    cliente_documento: str
    cliente_nombre: str
    prestamo_codigo: str
    metodo: str
    cuotas_totales: int
    pago: Pago
    tasa_cambio: bool  # ¿la tasa cambió respecto al recibo anterior?
    tasa_anterior: Decimal | None

    @property
    def total(self) -> Decimal:
        return self.pago.total_pagado


class GeneradorRecibos:
    def __init__(self, numeracion: Numeracion):
        self._numeracion = numeracion  # DIP: depende del contrato, no de una clase concreta

    def generar(self, prestamo: Prestamo, pago: Pago, fecha_emision: date | None = None) -> Recibo:
        previos = prestamo.pagos[:-1]
        tasa_anterior = previos[-1].tasa_anual if previos else None
        cambio = tasa_anterior is not None and tasa_anterior != pago.tasa_anual
        return Recibo(
            numero=self._numeracion.siguiente(),
            fecha_emision=fecha_emision or pago.fecha_pago,
            cliente_documento=prestamo.cliente.documento,
            cliente_nombre=prestamo.cliente.nombre,
            prestamo_codigo=prestamo.codigo,
            metodo=prestamo.metodo.nombre,
            cuotas_totales=prestamo.plazo_meses,
            pago=pago,
            tasa_cambio=cambio,
            tasa_anterior=tasa_anterior,
        )
