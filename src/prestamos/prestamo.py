"""El préstamo: encapsula su saldo y calcula cada cuota con la tasa vigente.

Relaciones de clases que se practican aquí:
  * COMPOSICIÓN  -> ``HistorialTasas`` nace y muere con el préstamo (se crea en __init__).
  * ASOCIACIÓN   -> ``Cliente`` existe antes y después del préstamo.
  * ESTRATEGIA   -> ``MetodoAmortizacion`` se recibe de fuera (se puede cambiar de método
                    sin subclasear Prestamo).
  * ENCAPSULAMIENTO -> el saldo es privado; solo cambia al aplicar un pago.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

from .amortizacion import MetodoAmortizacion
from .clientes import Cliente
from .dinero import dinero
from .excepciones import DatoInvalidoError, PagoInvalidoError
from .fechas import sumar_meses
from .tasas import HistorialTasas, TramoTasa


class EstadoPrestamo(Enum):
    VIGENTE = "Vigente"
    CANCELADO = "Cancelado"


@dataclass(frozen=True)
class PoliticaMora:
    """Interés moratorio simple: tasa anual sobre 360 días, con días de gracia."""

    tasa_anual: Decimal = Decimal("24")
    dias_gracia: int = 5

    def calcular(self, cuota: Decimal, dias_atraso: int) -> Decimal:
        if dias_atraso <= self.dias_gracia:
            return Decimal("0.00")
        return dinero(cuota * self.tasa_anual / Decimal(36000) * dias_atraso)


@dataclass(frozen=True)
class Pago:
    """Resultado inmutable de aplicar una cuota (base del recibo)."""

    numero_cuota: int
    fecha_vencimiento: date
    fecha_pago: date
    tasa_anual: Decimal
    saldo_anterior: Decimal
    interes: Decimal
    capital: Decimal
    mora: Decimal
    saldo_nuevo: Decimal

    @property
    def cuota(self) -> Decimal:
        return self.interes + self.capital

    @property
    def total_pagado(self) -> Decimal:
        return self.cuota + self.mora


@dataclass(frozen=True)
class LineaProyeccion:
    numero_cuota: int
    fecha_vencimiento: date
    tasa_anual: Decimal
    interes: Decimal
    capital: Decimal
    saldo_final: Decimal

    @property
    def cuota(self) -> Decimal:
        return self.interes + self.capital


class Prestamo:
    def __init__(
        self,
        codigo: str,
        cliente: Cliente,
        monto,
        plazo_meses: int,
        fecha_desembolso: date,
        tasa_anual,
        metodo: MetodoAmortizacion,
        politica_mora: PoliticaMora | None = None,
    ):
        monto = dinero(monto)
        if monto <= 0:
            raise DatoInvalidoError("El monto debe ser mayor que cero")
        if not isinstance(plazo_meses, int) or plazo_meses <= 0:
            raise DatoInvalidoError("El plazo debe ser un número entero de meses > 0")
        self._codigo = codigo
        self._cliente = cliente
        self._monto = monto
        self._plazo = plazo_meses
        self._desembolso = fecha_desembolso
        self._metodo = metodo
        self._mora = politica_mora or PoliticaMora()
        self._historial = HistorialTasas(tasa_anual, fecha_desembolso)  # COMPOSICIÓN
        self._saldo = monto
        self._cuotas_pagadas = 0
        self._pagos: list[Pago] = []

    # ---- lectura (propiedades de solo lectura) -------------------------------
    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def monto(self) -> Decimal:
        return self._monto

    @property
    def plazo_meses(self) -> int:
        return self._plazo

    @property
    def fecha_desembolso(self) -> date:
        return self._desembolso

    @property
    def saldo(self) -> Decimal:
        return self._saldo

    @property
    def cuotas_pagadas(self) -> int:
        return self._cuotas_pagadas

    @property
    def cuotas_restantes(self) -> int:
        return self._plazo - self._cuotas_pagadas

    @property
    def estado(self) -> EstadoPrestamo:
        return EstadoPrestamo.CANCELADO if self._saldo == 0 else EstadoPrestamo.VIGENTE

    @property
    def metodo(self) -> MetodoAmortizacion:
        return self._metodo

    @property
    def pagos(self) -> tuple[Pago, ...]:
        return tuple(self._pagos)

    # ---- tasa cambiante -------------------------------------------------------
    def registrar_tasa(self, desde: date, tasa_anual) -> TramoTasa:
        """Registra un cambio de tasa; afecta a las cuotas que VENZAN desde esa fecha."""
        return self._historial.registrar(desde, tasa_anual)

    def tasa_en(self, fecha: date) -> Decimal:
        return self._historial.tasa_en(fecha)

    def tramos_de_tasa(self) -> tuple[TramoTasa, ...]:
        return self._historial.tramos()

    # ---- cuotas ----------------------------------------------------------------
    def vencimiento(self, numero_cuota: int) -> date:
        return sumar_meses(self._desembolso, numero_cuota)

    def aplicar_pago(self, fecha_pago: date) -> Pago:
        """Aplica la PRÓXIMA cuota. La tasa es la vigente en la fecha de vencimiento."""
        if self.estado is EstadoPrestamo.CANCELADO:
            raise PagoInvalidoError(f"El préstamo {self._codigo} ya está cancelado")
        if fecha_pago < self._desembolso:
            raise PagoInvalidoError("La fecha de pago es anterior al desembolso")
        numero = self._cuotas_pagadas + 1
        vence = self.vencimiento(numero)
        tasa_anual = self._historial.tasa_en(vence)
        desglose = self._metodo.desglosar(
            self._saldo, self._historial.tasa_mensual_en(vence), self.cuotas_restantes
        )
        dias_atraso = (fecha_pago - vence).days
        mora = self._mora.calcular(desglose.total, max(dias_atraso, 0))
        saldo_nuevo = self._saldo - desglose.capital
        pago = Pago(
            numero,
            vence,
            fecha_pago,
            tasa_anual,
            self._saldo,
            desglose.interes,
            desglose.capital,
            mora,
            saldo_nuevo,
        )
        self._saldo = saldo_nuevo  # única vía por la que cambia el saldo
        self._cuotas_pagadas = numero
        self._pagos.append(pago)
        return pago

    def proyeccion(self) -> list[LineaProyeccion]:
        """Tabla de las cuotas que faltan SIN modificar el préstamo.

        Usa las tasas ya registradas; si luego cambia la tasa, hay que volver a proyectar.
        """
        lineas = []
        saldo = self._saldo
        for numero in range(self._cuotas_pagadas + 1, self._plazo + 1):
            vence = self.vencimiento(numero)
            restantes = self._plazo - numero + 1
            d = self._metodo.desglosar(saldo, self._historial.tasa_mensual_en(vence), restantes)
            saldo -= d.capital
            lineas.append(
                LineaProyeccion(
                    numero, vence, self._historial.tasa_en(vence), d.interes, d.capital, saldo
                )
            )
        return lineas
