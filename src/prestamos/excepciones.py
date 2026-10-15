"""Jerarquía de excepciones del dominio.

Aquí la HERENCIA es correcta: cada excepción específica ES-UN ``ErrorDominio``,
y quien captura ``ErrorDominio`` puede tratar cualquiera de ellas sin conocerlas.
"""


class ErrorDominio(Exception):
    """Base de todos los errores de negocio del sistema."""


class DatoInvalidoError(ErrorDominio):
    """Un dato de entrada no cumple las reglas (monto negativo, plazo cero...)."""


class TasaInvalidaError(DatoInvalidoError):
    """La tasa de interés o su fecha de vigencia no son válidas."""


class PagoInvalidoError(ErrorDominio):
    """El pago no se puede aplicar (préstamo cancelado, fecha anterior al desembolso...)."""


class NoEncontradoError(ErrorDominio):
    """No existe el préstamo o el cliente buscado."""
