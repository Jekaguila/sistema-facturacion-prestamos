from datetime import date
from decimal import Decimal

import pytest

from prestamos import (
    GeneradorRecibos,
    LineaExenta,
    LineaGravada,
    SecuenciaNumeracion,
    obtener_formateador,
)
from prestamos.excepciones import DatoInvalidoError
from prestamos.facturas import Factura
from prestamos.formatos import formatos_disponibles


def test_numeracion_consecutiva():
    s = SecuenciaNumeracion("R")
    assert (s.siguiente(), s.siguiente()) == ("R-000001", "R-000002")


def test_recibo_marca_cambio_de_tasa(prestamo):
    gen = GeneradorRecibos(SecuenciaNumeracion())
    r1 = gen.generar(prestamo, prestamo.aplicar_pago(date(2026, 2, 15)))
    assert r1.tasa_cambio is False
    prestamo.registrar_tasa(date(2026, 3, 1), 20)
    r2 = gen.generar(prestamo, prestamo.aplicar_pago(date(2026, 3, 15)))
    assert r2.tasa_cambio is True and r2.tasa_anterior == Decimal("12")


def test_recibo_es_inmutable(prestamo):
    r = GeneradorRecibos(SecuenciaNumeracion()).generar(
        prestamo, prestamo.aplicar_pago(date(2026, 2, 15))
    )
    with pytest.raises(Exception):
        r.numero = "otro"


def test_formatos_registrados_y_desconocido():
    assert formatos_disponibles() == ["csv", "json", "txt"]
    with pytest.raises(ValueError):
        obtener_formateador("pdf")


@pytest.mark.parametrize(
    "formato,fragmento",
    [("txt", "RECIBO DE PAGO"), ("json", '"total"'), ("csv", "recibo,prestamo")],
)
def test_cada_formato_produce_contenido(prestamo, formato, fragmento):
    r = GeneradorRecibos(SecuenciaNumeracion()).generar(
        prestamo, prestamo.aplicar_pago(date(2026, 2, 15))
    )
    assert fragmento in obtener_formateador(formato).formatear(r)


def test_factura_con_iva_y_linea_exenta():
    f = Factura("F-1", date(2026, 1, 15), "1", "Ana")
    f.agregar(LineaGravada("Comisión", 100))
    f.agregar(LineaExenta("Interés", 50))
    assert (f.subtotal, f.iva, f.total) == (Decimal("150.00"), Decimal("13.00"), Decimal("163.00"))


def test_linea_rechaza_base_no_positiva():
    with pytest.raises(DatoInvalidoError):
        LineaGravada("x", 0)
