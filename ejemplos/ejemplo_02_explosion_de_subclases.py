"""EJEMPLO 2 · Explosión de subclases (INCORRECTO) frente a composición con Estrategia (CORRECTO).

Problema: los préstamos varían en DOS ejes (método de amortización × tipo de tasa).
Con herencia hay que crear una subclase por cada combinación; con composición se
combinan piezas pequeñas en tiempo de ejecución.
Ejecutar:  python ejemplos/ejemplo_02_explosion_de_subclases.py
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: una subclase por combinación (2 × 2 = 4 clases; con 3 × 3 serían 9)
# ---------------------------------------------------------------------------
class PrestamoBase:
    def __init__(self, monto, plazo):
        self.monto, self.plazo = monto, plazo


class PrestamoFrancesTasaFija(PrestamoBase):
    def cuota(self):
        return "francés + tasa fija"


class PrestamoFrancesTasaVariable(PrestamoBase):
    def cuota(self):
        return "francés + tasa variable"


class PrestamoCapitalConstanteTasaFija(PrestamoBase):
    def cuota(self):
        return "capital constante + tasa fija"


class PrestamoCapitalConstanteTasaVariable(PrestamoBase):
    def cuota(self):
        return "capital constante + tasa variable"


# ---------------------------------------------------------------------------
# ✅ CORRECTO: UNA clase Prestamo que TIENE un método y TIENE una política de tasa
# ---------------------------------------------------------------------------
class Metodo(ABC):
    @abstractmethod
    def nombre(self): ...


class Frances(Metodo):
    def nombre(self):
        return "francés"


class CapitalConstante(Metodo):
    def nombre(self):
        return "capital constante"


class PoliticaTasa(ABC):
    @abstractmethod
    def nombre(self): ...


class TasaFija(PoliticaTasa):
    def nombre(self):
        return "tasa fija"


class TasaVariable(PoliticaTasa):
    def nombre(self):
        return "tasa variable"


class Prestamo:
    def __init__(self, monto, plazo, metodo: Metodo, politica: PoliticaTasa):
        self.monto, self.plazo = monto, plazo
        self._metodo, self._politica = metodo, politica  # composición

    def describir(self):
        return f"{self._metodo.nombre()} + {self._politica.nombre()}"


if __name__ == "__main__":
    mala = [
        PrestamoFrancesTasaFija,
        PrestamoFrancesTasaVariable,
        PrestamoCapitalConstanteTasaFija,
        PrestamoCapitalConstanteTasaVariable,
    ]
    print("❌ Herencia: 2 métodos × 2 tasas =", len(mala), "subclases.")
    print("   Si se agrega un método nuevo hay que escribir 2 clases más.\n")

    metodos = [Frances(), CapitalConstante()]
    politicas = [TasaFija(), TasaVariable()]
    print("✅ Composición: 1 clase Prestamo + 2 métodos + 2 políticas = 5 clases pequeñas.")
    for m in metodos:
        for t in politicas:
            print("  ", Prestamo(1000, 12, m, t).describir())
    print("   Un método nuevo = 1 clase nueva; las combinaciones salen solas.")
