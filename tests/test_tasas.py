from datetime import date
from decimal import Decimal

import pytest

from prestamos.excepciones import TasaInvalidaError
from prestamos.tasas import HistorialTasas


def test_tasa_vigente_segun_fecha():
    h = HistorialTasas(12, date(2026, 1, 15))
    h.registrar(date(2026, 5, 1), 18)
    assert h.tasa_en(date(2026, 4, 30)) == Decimal("12")
    assert h.tasa_en(date(2026, 5, 1)) == Decimal("18")
    assert h.tasa_en(date(2027, 1, 1)) == Decimal("18")


def test_tasa_mensual():
    assert HistorialTasas(12, date(2026, 1, 1)).tasa_mensual_en(date(2026, 2, 1)) == Decimal("0.01")


@pytest.mark.parametrize("tasa", [-1, 101, "abc"])
def test_rechaza_tasas_invalidas(tasa):
    with pytest.raises(TasaInvalidaError):
        HistorialTasas(tasa, date(2026, 1, 1))


def test_cambio_debe_ser_posterior():
    h = HistorialTasas(12, date(2026, 1, 15))
    with pytest.raises(TasaInvalidaError):
        h.registrar(date(2026, 1, 15), 15)


def test_tramos_devuelve_copia_inmutable():
    h = HistorialTasas(12, date(2026, 1, 15))
    assert isinstance(h.tramos(), tuple)
