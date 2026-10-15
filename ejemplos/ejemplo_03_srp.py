"""EJEMPLO 3 · S — Responsabilidad Única (SRP).

«Una clase debe tener una sola razón para cambiar.»
Ejecutar:  python ejemplos/ejemplo_03_srp.py
"""

import json
from dataclasses import dataclass
from decimal import Decimal


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: la clase calcula, imprime Y guarda → 3 razones para cambiar
# ---------------------------------------------------------------------------
class ReciboMalo:
    def __init__(self, saldo, tasa_anual):
        self.saldo, self.tasa_anual = Decimal(saldo), Decimal(tasa_anual)

    def calcular_interes(self):  # razón 1: la regla de negocio
        return (self.saldo * self.tasa_anual / 1200).quantize(Decimal("0.01"))

    def imprimir(self):  # razón 2: el formato de salida
        return f"RECIBO  interés: ${self.calcular_interes()}"

    def guardar(self, almacen):  # razón 3: el medio de almacenamiento
        almacen.append(json.dumps({"interes": str(self.calcular_interes())}))


# ---------------------------------------------------------------------------
# ✅ CORRECTO: cada clase tiene UNA razón de cambio
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Recibo:  # datos
    interes: Decimal


class CalculadoraInteres:  # regla de negocio
    def calcular(self, saldo, tasa_anual) -> Recibo:
        interes = (Decimal(saldo) * Decimal(tasa_anual) / 1200).quantize(Decimal("0.01"))
        return Recibo(interes)


class ReciboTexto:  # presentación
    def formatear(self, r: Recibo) -> str:
        return f"RECIBO  interés: ${r.interes}"


class AlmacenJSON:  # persistencia
    def guardar(self, r: Recibo, destino: list) -> None:
        destino.append(json.dumps({"interes": str(r.interes)}))


if __name__ == "__main__":
    destino = []
    print("❌ Una sola clase hace todo:")
    m = ReciboMalo(1000, 12)
    print("  ", m.imprimir())
    print("   Si cambia el formato (HTML), si cambia el almacén (BD) o si cambia la fórmula,")
    print("   hay que abrir y modificar LA MISMA clase → riesgo de romper lo que ya funciona.\n")

    print("✅ Clases con una responsabilidad:")
    r = CalculadoraInteres().calcular(1000, 12)
    print("  ", ReciboTexto().formatear(r))
    AlmacenJSON().guardar(r, destino)
    print("   Guardado:", destino[0])
    print(
        "   Cambiar el formato solo toca ReciboTexto; cambiar la fórmula solo toca CalculadoraInteres."
    )
