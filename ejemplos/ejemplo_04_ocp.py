"""EJEMPLO 4 · O — Abierto/Cerrado (OCP).

«Abierto para extensión, cerrado para modificación.»
Ejecutar:  python ejemplos/ejemplo_04_ocp.py
"""

from abc import ABC, abstractmethod
from decimal import Decimal


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: cada tipo nuevo obliga a EDITAR la función (y a volver a probarla toda)
# ---------------------------------------------------------------------------
def cuota_mala(tipo, saldo, tasa_mensual, k):
    if tipo == "frances":
        return round(saldo * tasa_mensual / (1 - (1 + tasa_mensual) ** -k), 2)
    elif tipo == "capital_constante":
        return round(saldo / k + saldo * tasa_mensual, 2)
    # Para añadir "solo_intereses" hay que modificar esta función… y olvidar un elif
    # devuelve None sin avisar:
    return None


# ---------------------------------------------------------------------------
# ✅ CORRECTO: se EXTIENDE agregando clases; la función que las usa no cambia
# ---------------------------------------------------------------------------
class Metodo(ABC):
    @abstractmethod
    def cuota(self, saldo: Decimal, r: Decimal, k: int) -> Decimal: ...


class Frances(Metodo):
    def cuota(self, saldo, r, k):
        return (saldo * r / (1 - (1 + r) ** -k)).quantize(Decimal("0.01"))


class CapitalConstante(Metodo):
    def cuota(self, saldo, r, k):
        return (saldo / k + saldo * r).quantize(Decimal("0.01"))


def calcular(metodo: Metodo, saldo, r, k):  # NO se toca nunca
    return metodo.cuota(Decimal(saldo), Decimal(r), k)


# ← Extensión: una clase nueva, cero líneas modificadas arriba
class SoloIntereses(Metodo):
    def cuota(self, saldo, r, k):
        return (saldo * r).quantize(Decimal("0.01"))


if __name__ == "__main__":
    print("❌ if/elif:")
    print("   frances            →", cuota_mala("frances", 1000, 0.01, 12))
    print(
        "   solo_intereses     →",
        cuota_mala("solo_intereses", 1000, 0.01, 12),
        "← devuelve None en silencio; hay que editar la función",
    )

    print("\n✅ Polimorfismo + extensión:")
    for m in (Frances(), CapitalConstante(), SoloIntereses()):
        print(f"   {m.__class__.__name__:<17} →", calcular(m, 1000, "0.01", 12))
    print("   SoloIntereses se añadió sin modificar `calcular` ni las otras clases.")
