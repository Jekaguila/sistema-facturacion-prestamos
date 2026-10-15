from datetime import date
from decimal import Decimal

import pytest

from prestamos import CapitalConstante, EstadoPrestamo, FrancesCuotaFija, Prestamo
from prestamos.excepciones import DatoInvalidoError, PagoInvalidoError


def pagar_todo(p, desde_fecha=None):
    for n in range(1, p.plazo_meses + 1):
        p.aplicar_pago(p.vencimiento(n))


def test_primera_cuota_francesa_12_por_ciento(prestamo):
    pago = prestamo.aplicar_pago(date(2026, 2, 15))
    assert pago.interes == Decimal("12.00")  # 1 200 * 1 %
    assert pago.cuota == Decimal("106.62")  # cuota fija del sistema francés
    assert pago.capital == Decimal("94.62")
    assert pago.saldo_nuevo == Decimal("1105.38")


def test_saldo_queda_en_cero_y_se_cancela(prestamo):
    pagar_todo(prestamo)
    assert prestamo.saldo == Decimal("0.00")
    assert prestamo.estado is EstadoPrestamo.CANCELADO
    assert sum(p.capital for p in prestamo.pagos) == Decimal("1200.00")


def test_cambio_de_tasa_recalcula_la_cuota(prestamo):
    for n in (1, 2, 3):
        prestamo.aplicar_pago(prestamo.vencimiento(n))
    cuota_antes = prestamo.pagos[-1].cuota
    prestamo.registrar_tasa(date(2026, 5, 1), 18)
    pago = prestamo.aplicar_pago(date(2026, 5, 15))
    assert pago.tasa_anual == Decimal("18")
    assert pago.cuota > cuota_antes
    pagar_todo_restante = [prestamo.aplicar_pago(prestamo.vencimiento(n)) for n in range(5, 13)]
    assert pagar_todo_restante[-1].saldo_nuevo == Decimal("0.00")


def test_la_tasa_aplicada_es_la_del_vencimiento_no_la_del_pago(prestamo):
    prestamo.registrar_tasa(date(2026, 2, 20), 30)  # cambia DESPUÉS de vencer la cuota 1
    pago = prestamo.aplicar_pago(date(2026, 3, 1))  # se paga tarde, pero vencía el 15-feb
    assert pago.tasa_anual == Decimal("12")


def test_mora_con_gracia(prestamo):
    a_tiempo = prestamo.aplicar_pago(date(2026, 2, 20))  # 5 días: dentro de la gracia
    assert a_tiempo.mora == Decimal("0.00")
    tarde = prestamo.aplicar_pago(date(2026, 3, 25))  # 10 días de atraso
    assert tarde.mora > 0


def test_pago_adelantado_no_genera_mora(prestamo):
    assert prestamo.aplicar_pago(date(2026, 2, 1)).mora == Decimal("0.00")


def test_no_se_puede_pagar_un_prestamo_cancelado(prestamo):
    pagar_todo(prestamo)
    with pytest.raises(PagoInvalidoError):
        prestamo.aplicar_pago(date(2027, 2, 1))


def test_pago_antes_del_desembolso(prestamo):
    with pytest.raises(PagoInvalidoError):
        prestamo.aplicar_pago(date(2026, 1, 1))


@pytest.mark.parametrize("monto,plazo", [(0, 12), (-5, 12), (1000, 0), (1000, 1.5)])
def test_datos_invalidos(cliente, monto, plazo):
    with pytest.raises(DatoInvalidoError):
        Prestamo("X", cliente, monto, plazo, date(2026, 1, 1), 12, FrancesCuotaFija())


def test_saldo_es_solo_lectura(prestamo):
    with pytest.raises(AttributeError):
        prestamo.saldo = 0


def test_proyeccion_no_modifica_el_prestamo(prestamo):
    saldo = prestamo.saldo
    tabla = prestamo.proyeccion()
    assert len(tabla) == 12
    assert prestamo.saldo == saldo and prestamo.cuotas_pagadas == 0
    assert tabla[-1].saldo_final == Decimal("0.00")


def test_proyeccion_coincide_con_pagos_reales(prestamo):
    tabla = prestamo.proyeccion()
    reales = [prestamo.aplicar_pago(prestamo.vencimiento(n)) for n in range(1, 13)]
    assert [fila.cuota for fila in tabla] == [r.cuota for r in reales]


def test_tasa_cero_francesa(cliente):
    p = Prestamo("Z", cliente, 1200, 12, date(2026, 1, 1), 0, FrancesCuotaFija())
    assert p.aplicar_pago(date(2026, 2, 1)).cuota == Decimal("100.00")


def test_capital_constante_baja_el_interes(cliente):
    p = Prestamo("C", cliente, 1200, 12, date(2026, 1, 15), 12, CapitalConstante())
    primero, segundo = [p.aplicar_pago(p.vencimiento(n)) for n in (1, 2)]
    assert primero.capital == segundo.capital == Decimal("100.00")
    assert segundo.interes < primero.interes


@pytest.mark.parametrize("metodo", [FrancesCuotaFija(), CapitalConstante()], ids=lambda m: m.nombre)
def test_contrato_lsp_cualquier_metodo_liquida_el_prestamo(cliente, metodo):
    """LSP: todo MetodoAmortizacion es intercambiable; ninguno rompe el contrato."""
    p = Prestamo("L", cliente, 1000, 7, date(2026, 1, 31), 15, metodo)
    p.registrar_tasa(date(2026, 4, 1), 22)
    pagos = [p.aplicar_pago(p.vencimiento(n)) for n in range(1, 8)]
    assert p.saldo == Decimal("0.00")
    assert sum(x.capital for x in pagos) == Decimal("1000.00")
    assert all(x.capital > 0 and x.saldo_nuevo >= 0 for x in pagos)
