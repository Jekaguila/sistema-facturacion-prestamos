"""Facturas de cargos (comisión, mora...).

Los intereses y el capital se prueban con el RECIBO. La FACTURA se usa para cobros
por servicios (comisión de apertura, cargo por mora...). El tratamiento tributario
aquí es DIDÁCTICO: en un sistema real se parametriza según la ley vigente.

Aquí la HERENCIA es correcta: ``LineaGravada`` y ``LineaExenta`` SON-UNA ``LineaFactura``
y se pueden usar indistintamente (polimorfismo con ``impuesto()``).
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from .dinero import dinero
from .excepciones import DatoInvalidoError


class LineaFactura(ABC):
    def __init__(self, descripcion: str, base):
        base = dinero(base)
        if base <= 0:
            raise DatoInvalidoError("La base de una línea debe ser mayor que cero")
        self.descripcion = descripcion
        self._base = base

    @property
    def base(self) -> Decimal:
        return self._base

    @abstractmethod
    def impuesto(self) -> Decimal:
        """Impuesto de esta línea."""

    def total(self) -> Decimal:
        return self._base + self.impuesto()


class LineaGravada(LineaFactura):
    TASA_IVA = Decimal("0.13")

    def impuesto(self) -> Decimal:
        return dinero(self._base * self.TASA_IVA)


class LineaExenta(LineaFactura):
    def impuesto(self) -> Decimal:
        return Decimal("0.00")


class Factura:
    def __init__(self, numero: str, fecha: date, cliente_documento: str, cliente_nombre: str):
        self.numero = numero
        self.fecha = fecha
        self.cliente_documento = cliente_documento
        self.cliente_nombre = cliente_nombre
        self._lineas: list[LineaFactura] = []

    def agregar(self, linea: LineaFactura) -> None:
        self._lineas.append(linea)

    @property
    def lineas(self) -> tuple[LineaFactura, ...]:
        return tuple(self._lineas)

    @property
    def subtotal(self) -> Decimal:
        return sum((linea.base for linea in self._lineas), Decimal("0.00"))

    @property
    def iva(self) -> Decimal:
        return sum((linea.impuesto() for linea in self._lineas), Decimal("0.00"))

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.iva
