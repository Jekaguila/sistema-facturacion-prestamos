from datetime import date
from decimal import Decimal

import pytest

from prestamos import FrancesCuotaFija
from prestamos.excepciones import NoEncontradoError


def crear(servicio, cliente):
    return servicio.crear_prestamo(
        "P-001", cliente, 1200, 12, date(2026, 1, 15), 12, FrancesCuotaFija()
    )


def test_flujo_completo_con_cambio_de_tasa(servicio, cliente):
    crear(servicio, cliente)
    for mes in (2, 3, 4):
        servicio.cobrar_cuota("P-001", date(2026, mes, 15))
    servicio.cambiar_tasa("P-001", date(2026, 5, 1), 18)
    recibo, ruta = servicio.cobrar_cuota("P-001", date(2026, 5, 15))
    assert recibo.numero == "R-000004" and recibo.tasa_cambio
    assert ruta == "R-000004.txt"


def test_prestamo_inexistente(servicio):
    with pytest.raises(NoEncontradoError):
        servicio.cobrar_cuota("NO-EXISTE", date(2026, 2, 15))


def test_factura_de_comision(servicio, cliente):
    p = crear(servicio, cliente)
    f = servicio.facturar_cargos(p, date(2026, 1, 15))
    assert (
        f.subtotal == Decimal("18.00") and f.iva == Decimal("2.34") and f.total == Decimal("20.34")
    )


def test_factura_de_mora_solo_si_hay_mora(servicio, cliente):
    p = crear(servicio, cliente)
    recibo, _ = servicio.cobrar_cuota("P-001", date(2026, 3, 20))  # 33 días de atraso
    assert recibo.pago.mora > 0
    assert len(servicio.facturar_cargos(p, date(2026, 3, 20), recibo.pago).lineas) == 1
    recibo2, _ = servicio.cobrar_cuota("P-001", date(2026, 3, 15))
    assert servicio.facturar_cargos(p, date(2026, 3, 20), recibo2.pago) is None
