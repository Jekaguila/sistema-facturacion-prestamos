"""EJEMPLO 5 · L — Sustitución de Liskov (LSP).

«Donde se espera un objeto de la clase base, cualquier subclase debe poder usarse sin sorpresas.»
Ejecutar:  python ejemplos/ejemplo_05_lsp.py
"""

from abc import ABC
from decimal import Decimal


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: la subclase rompe el contrato de la base
# ---------------------------------------------------------------------------
class CuentaMala:
    def __init__(self, saldo):
        self.saldo = Decimal(saldo)

    def retirar(self, monto):
        self.saldo -= Decimal(monto)
        return self.saldo


class CuentaPlazoFijoMala(CuentaMala):
    def retirar(self, monto):  # ¡la base prometía poder retirar!
        raise RuntimeError("Un plazo fijo no admite retiros")


def cobrar_comision_mala(cuentas):
    for c in cuentas:
        c.retirar(1)  # el código cliente confía en la base


# ---------------------------------------------------------------------------
# ✅ CORRECTO: el contrato se divide según lo que cada tipo REALMENTE puede hacer
# ---------------------------------------------------------------------------
class Cuenta(ABC):
    def __init__(self, saldo):
        self._saldo = Decimal(saldo)

    @property
    def saldo(self):
        return self._saldo


class CuentaRetirable(Cuenta):
    def retirar(self, monto):
        monto = Decimal(monto)
        if monto > self._saldo:
            raise ValueError("Fondos insuficientes")
        self._saldo -= monto
        return self._saldo


class CuentaPlazoFijo(Cuenta):  # no promete retirar; no hereda ese contrato
    def vencer(self):
        return self._saldo


def cobrar_comision(cuentas: list[CuentaRetirable]):
    for c in cuentas:
        c.retirar(1)


if __name__ == "__main__":
    print("❌ Subclase que rompe el contrato:")
    try:
        cobrar_comision_mala([CuentaMala(100), CuentaPlazoFijoMala(100)])
    except RuntimeError as error:
        print("   ¡Explotó al recorrer la lista!", error)
        print("   El código que usa CuentaMala ya no puede confiar en sus subclases.\n")

    print("✅ Cada tipo promete solo lo que cumple:")
    cuentas = [CuentaRetirable(100), CuentaRetirable(50)]
    cobrar_comision(cuentas)
    print("   Saldos tras la comisión:", [str(c.saldo) for c in cuentas])
    print(
        "   Plazo fijo vence con:",
        CuentaPlazoFijo(100).vencer(),
        "(nunca entra a la lista de «retirables»)",
    )
