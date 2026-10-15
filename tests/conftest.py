from datetime import date

import pytest

from prestamos import (
    AlmacenMemoria,
    Cliente,
    FrancesCuotaFija,
    GeneradorRecibos,
    Prestamo,
    RepositorioMemoria,
    SecuenciaNumeracion,
    ServicioPrestamos,
    obtener_formateador,
)


@pytest.fixture
def cliente():
    return Cliente("04567891-2", "María Contreras")


@pytest.fixture
def prestamo(cliente):
    """1 200 a 12 meses, 12 % anual, desembolso el 15-ene-2026."""
    return Prestamo("P-001", cliente, 1200, 12, date(2026, 1, 15), 12, FrancesCuotaFija())


@pytest.fixture
def servicio():
    return ServicioPrestamos(
        RepositorioMemoria(),
        GeneradorRecibos(SecuenciaNumeracion("R")),
        AlmacenMemoria(),
        obtener_formateador("txt"),
        SecuenciaNumeracion("F"),
    )
