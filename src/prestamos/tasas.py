"""Historial de tasas de interés (tasa CAMBIANTE del préstamo).

``HistorialTasas`` es una pieza que el préstamo CONTIENE y controla
(composición): nadie fuera del préstamo la crea ni la modifica a su gusto.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from .excepciones import TasaInvalidaError

TASA_MAXIMA = Decimal("100")  # % anual; evita errores de digitación (ej. 1800 en vez de 18)


def _a_tasa(valor) -> Decimal:
    try:
        tasa = Decimal(str(valor))
    except InvalidOperation as error:
        raise TasaInvalidaError(f"Tasa no numérica: {valor!r}") from error
    if not (Decimal("0") <= tasa <= TASA_MAXIMA):
        raise TasaInvalidaError(f"La tasa debe estar entre 0 y {TASA_MAXIMA} % anual")
    return tasa


@dataclass(frozen=True)
class TramoTasa:
    """Una tasa anual (en %) que rige desde ``desde`` hasta el siguiente cambio."""

    desde: date
    tasa_anual: Decimal


class HistorialTasas:
    """Lista ordenada de tramos; permite saber qué tasa regía en cualquier fecha."""

    def __init__(self, tasa_inicial, desde: date):
        self._tramos: list[TramoTasa] = [TramoTasa(desde, _a_tasa(tasa_inicial))]

    def registrar(self, desde: date, tasa_anual) -> TramoTasa:
        """Agrega un cambio de tasa. Debe ser posterior al último registrado."""
        if desde <= self._tramos[-1].desde:
            raise TasaInvalidaError(
                f"El cambio debe ser posterior al {self._tramos[-1].desde.isoformat()}"
            )
        tramo = TramoTasa(desde, _a_tasa(tasa_anual))
        self._tramos.append(tramo)
        return tramo

    def tasa_en(self, fecha: date) -> Decimal:
        """Tasa anual (%) vigente en ``fecha``."""
        if fecha < self._tramos[0].desde:
            raise TasaInvalidaError("No hay tasa vigente antes del desembolso")
        vigente = self._tramos[0]
        for tramo in self._tramos:
            if tramo.desde <= fecha:
                vigente = tramo
        return vigente.tasa_anual

    def tasa_mensual_en(self, fecha: date) -> Decimal:
        """Tasa mensual como fracción: 12 % anual -> 0.01."""
        return self.tasa_en(fecha) / Decimal(1200)

    def tramos(self) -> tuple[TramoTasa, ...]:
        """Copia inmutable del historial (el original no se puede alterar desde fuera)."""
        return tuple(self._tramos)
