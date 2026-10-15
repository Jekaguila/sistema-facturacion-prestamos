"""Métodos de amortización (patrón Estrategia).

Cada método decide cuánto de la cuota es interés y cuánto es capital. El préstamo
RECIBE un método (composición) en lugar de heredar de uno: así existe UNA sola clase
``Prestamo`` y cambiar de método no obliga a crear subclases.

Agregar un método nuevo (por ejemplo, "solo intereses") es AÑADIR una clase,
sin modificar ``Prestamo`` -> principio Abierto/Cerrado (OCP).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from .dinero import dinero


@dataclass(frozen=True)
class DesgloseCuota:
    interes: Decimal
    capital: Decimal

    @property
    def total(self) -> Decimal:
        return self.interes + self.capital


class MetodoAmortizacion(ABC):
    """Contrato: cualquier método debe poder desglosar la próxima cuota."""

    nombre = "abstracto"

    @abstractmethod
    def desglosar(
        self, saldo: Decimal, tasa_mensual: Decimal, cuotas_restantes: int
    ) -> DesgloseCuota:
        """Calcula interés y capital de la próxima cuota con la tasa VIGENTE."""

    @staticmethod
    def _ajustar_ultima(
        saldo: Decimal, interes: Decimal, capital: Decimal, cuotas_restantes: int
    ) -> DesgloseCuota:
        # Contrato común (LSP): el capital nunca supera el saldo y la última cuota lo liquida.
        if cuotas_restantes == 1 or capital > saldo:
            capital = saldo
        return DesgloseCuota(interes, capital)


class FrancesCuotaFija(MetodoAmortizacion):
    """Cuota constante, RECALCULADA con la tasa vigente y las cuotas que faltan.

    cuota = saldo * r / (1 - (1 + r) ** -k)      (r = tasa mensual, k = cuotas restantes)
    Si la tasa sube o baja, la cuota se recalcula y el plazo original se respeta.
    """

    nombre = "Francés (cuota fija recalculada)"

    def desglosar(self, saldo, tasa_mensual, cuotas_restantes):
        interes = dinero(saldo * tasa_mensual)
        if tasa_mensual == 0:
            cuota = dinero(saldo / cuotas_restantes)
        else:
            cuota = dinero(saldo * tasa_mensual / (1 - (1 + tasa_mensual) ** -cuotas_restantes))
        return self._ajustar_ultima(saldo, interes, cuota - interes, cuotas_restantes)


class CapitalConstante(MetodoAmortizacion):
    """Capital fijo por cuota; el interés baja conforme baja el saldo."""

    nombre = "Capital constante"

    def desglosar(self, saldo, tasa_mensual, cuotas_restantes):
        interes = dinero(saldo * tasa_mensual)
        capital = dinero(saldo / cuotas_restantes)
        return self._ajustar_ultima(saldo, interes, capital, cuotas_restantes)
