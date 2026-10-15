"""Formatos de salida del recibo y de la factura.

Principio Abierto/Cerrado (OCP): para soportar un formato nuevo basta con escribir
una clase y decorarla con ``@formato_recibo("html")``; ninguna otra línea del sistema cambia.

Principio de Segregación de Interfaces (ISP): el contrato es MÍNIMO (dos miembros);
quien formatea no está obligado a saber guardar, enviar ni imprimir.
"""

import csv
import io
import json
from typing import Protocol

from .dinero import fmt
from .facturas import Factura
from .recibos import Recibo


class FormateadorRecibo(Protocol):
    extension: str

    def formatear(self, recibo: Recibo) -> str: ...


_FORMATOS: dict[str, type] = {}


def formato_recibo(nombre: str):
    """Decorador de registro: añade un formato sin tocar el código existente."""

    def registrar(clase):
        _FORMATOS[nombre] = clase
        return clase

    return registrar


def obtener_formateador(nombre: str) -> FormateadorRecibo:
    try:
        return _FORMATOS[nombre]()
    except KeyError:
        raise ValueError(
            f"Formato desconocido: {nombre!r}. Disponibles: {sorted(_FORMATOS)}"
        ) from None


def formatos_disponibles() -> list[str]:
    return sorted(_FORMATOS)


@formato_recibo("txt")
class ReciboTexto:
    extension = "txt"
    ANCHO = 46

    def formatear(self, r: Recibo) -> str:
        p = r.pago
        linea = "=" * self.ANCHO
        filas = [
            linea,
            "RECIBO DE PAGO DE CUOTA".center(self.ANCHO).rstrip(),
            linea,
            f"Recibo N.°   : {r.numero}",
            f"Fecha        : {r.fecha_emision.isoformat()}",
            f"Cliente      : {r.cliente_nombre} ({r.cliente_documento})",
            f"Préstamo     : {r.prestamo_codigo} · {r.metodo}",
            f"Cuota        : {p.numero_cuota} de {r.cuotas_totales}",
            f"Vencimiento  : {p.fecha_vencimiento.isoformat()}",
            "-" * self.ANCHO,
            f"Tasa aplicada: {p.tasa_anual}% anual"
            + (f"  (antes {r.tasa_anterior}%) ← CAMBIÓ" if r.tasa_cambio else ""),
            f"Saldo anterior : {fmt(p.saldo_anterior):>14}",
            f"Interés        : {fmt(p.interes):>14}",
            f"Capital        : {fmt(p.capital):>14}",
            f"Mora           : {fmt(p.mora):>14}",
            "-" * self.ANCHO,
            f"TOTAL PAGADO   : {fmt(r.total):>14}",
            f"Saldo nuevo    : {fmt(p.saldo_nuevo):>14}",
            linea,
        ]
        return "\n".join(filas)


@formato_recibo("json")
class ReciboJSON:
    extension = "json"

    def formatear(self, r: Recibo) -> str:
        p = r.pago
        datos = {
            "numero": r.numero,
            "fecha": r.fecha_emision.isoformat(),
            "cliente": {"documento": r.cliente_documento, "nombre": r.cliente_nombre},
            "prestamo": r.prestamo_codigo,
            "cuota": p.numero_cuota,
            "vencimiento": p.fecha_vencimiento.isoformat(),
            "tasa_anual": str(p.tasa_anual),
            "tasa_cambio": r.tasa_cambio,
            "saldo_anterior": str(p.saldo_anterior),
            "interes": str(p.interes),
            "capital": str(p.capital),
            "mora": str(p.mora),
            "total": str(r.total),
            "saldo_nuevo": str(p.saldo_nuevo),
        }
        return json.dumps(datos, ensure_ascii=False, indent=2)


@formato_recibo("csv")
class ReciboCSV:
    extension = "csv"

    def formatear(self, r: Recibo) -> str:
        p = r.pago
        salida = io.StringIO()
        escritor = csv.writer(salida, lineterminator="\n")
        escritor.writerow(
            [
                "recibo",
                "prestamo",
                "cuota",
                "tasa_anual",
                "interes",
                "capital",
                "mora",
                "total",
                "saldo_nuevo",
            ]
        )
        escritor.writerow(
            [
                r.numero,
                r.prestamo_codigo,
                p.numero_cuota,
                p.tasa_anual,
                p.interes,
                p.capital,
                p.mora,
                r.total,
                p.saldo_nuevo,
            ]
        )
        return salida.getvalue()


def factura_a_texto(f: Factura) -> str:
    filas = [
        f"FACTURA {f.numero} · {f.fecha.isoformat()}",
        f"Cliente: {f.cliente_nombre} ({f.cliente_documento})",
        "-" * 46,
    ]
    for linea in f.lineas:
        filas.append(f"{linea.descripcion:<28}{fmt(linea.base):>9}  IVA {fmt(linea.impuesto()):>7}")
    filas += [
        "-" * 46,
        f"Subtotal {fmt(f.subtotal):>37}",
        f"IVA      {fmt(f.iva):>37}",
        f"TOTAL    {fmt(f.total):>37}",
    ]
    return "\n".join(filas)
