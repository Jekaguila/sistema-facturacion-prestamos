"""Caso de uso: orquesta las piezas sin conocer los detalles de ninguna.

Todas las dependencias llegan por el constructor (inyección de dependencias).
"""

from datetime import date
from decimal import Decimal

from .almacenes import AlmacenDocumentos, RepositorioPrestamos
from .amortizacion import MetodoAmortizacion
from .clientes import Cliente
from .dinero import dinero
from .facturas import Factura, LineaGravada
from .formatos import FormateadorRecibo, factura_a_texto
from .prestamo import Pago, Prestamo
from .recibos import GeneradorRecibos, Numeracion, Recibo


class ServicioPrestamos:
    COMISION_APERTURA = Decimal("0.015")  # 1.5 % del monto

    def __init__(
        self,
        repositorio: RepositorioPrestamos,
        generador: GeneradorRecibos,
        almacen: AlmacenDocumentos,
        formateador: FormateadorRecibo,
        numeracion_facturas: Numeracion,
    ):
        self._repo = repositorio
        self._recibos = generador
        self._almacen = almacen
        self._formateador = formateador
        self._facturas = numeracion_facturas

    def crear_prestamo(
        self,
        codigo: str,
        cliente: Cliente,
        monto,
        plazo_meses: int,
        fecha_desembolso: date,
        tasa_anual,
        metodo: MetodoAmortizacion,
    ) -> Prestamo:
        prestamo = Prestamo(
            codigo, cliente, monto, plazo_meses, fecha_desembolso, tasa_anual, metodo
        )
        self._repo.guardar(prestamo)
        return prestamo

    def cambiar_tasa(self, codigo: str, desde: date, tasa_anual) -> None:
        self._repo.obtener(codigo).registrar_tasa(desde, tasa_anual)

    def cobrar_cuota(self, codigo: str, fecha_pago: date) -> tuple[Recibo, str]:
        """Aplica la cuota, genera el recibo y lo guarda. Devuelve (recibo, ruta)."""
        prestamo = self._repo.obtener(codigo)
        pago: Pago = prestamo.aplicar_pago(fecha_pago)
        recibo = self._recibos.generar(prestamo, pago)
        nombre = f"{recibo.numero}.{self._formateador.extension}"
        ruta = self._almacen.guardar(nombre, self._formateador.formatear(recibo))
        return recibo, ruta

    def facturar_cargos(
        self, prestamo: Prestamo, fecha: date, pago: Pago | None = None
    ) -> Factura | None:
        """Factura la comisión de apertura (sin ``pago``) o el cargo por mora de un pago.

        Devuelve ``None`` si no hay nada que facturar (pago sin mora).
        """
        if pago is not None and pago.mora == 0:
            return None
        factura = Factura(
            self._facturas.siguiente(), fecha, prestamo.cliente.documento, prestamo.cliente.nombre
        )
        if pago is None:
            factura.agregar(
                LineaGravada(
                    "Comisión de apertura", dinero(prestamo.monto * self.COMISION_APERTURA)
                )
            )
        else:
            factura.agregar(LineaGravada(f"Mora cuota {pago.numero_cuota}", pago.mora))
        self._almacen.guardar(f"{factura.numero}.txt", factura_a_texto(factura))
        return factura

    def estado_de_cuenta(self, codigo: str) -> list[str]:
        p = self._repo.obtener(codigo)
        return [
            f"Préstamo {p.codigo} · {p.cliente.nombre}",
            f"Saldo {p.saldo} · cuotas pagadas {p.cuotas_pagadas}/{p.plazo_meses}",
            f"Estado: {p.estado.value}",
        ]
