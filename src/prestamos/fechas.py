"""Funciones de fecha sin dependencias externas."""

import calendar
from datetime import date


def sumar_meses(fecha: date, meses: int) -> date:
    """Suma ``meses`` a ``fecha`` ajustando el día al último del mes si hace falta.

    >>> sumar_meses(date(2026, 1, 31), 1)
    datetime.date(2026, 2, 28)
    """
    indice = fecha.month - 1 + meses
    anio = fecha.year + indice // 12
    mes = indice % 12 + 1
    dia = min(fecha.day, calendar.monthrange(anio, mes)[1])
    return date(anio, mes, dia)
