"""EJEMPLO 7 · D — Inversión de Dependencias (DIP) + inyección de dependencias.

«Depende de abstracciones, no de clases concretas.»
Ejecutar:  python ejemplos/ejemplo_07_dip.py
"""

from typing import Protocol


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: el servicio crea su propia dependencia concreta (no se puede probar sin disco)
# ---------------------------------------------------------------------------
class AlmacenArchivoMalo:
    def guardar(self, texto):
        raise OSError("sin permisos de escritura en /raiz/recibos")  # simula el disco


class ServicioMalo:
    def __init__(self):
        self._almacen = AlmacenArchivoMalo()  # acoplado a una clase concreta

    def cobrar(self):
        self._almacen.guardar("recibo")


# ---------------------------------------------------------------------------
# ✅ CORRECTO: el servicio depende de un contrato y la dependencia LLEGA desde fuera
# ---------------------------------------------------------------------------
class Almacen(Protocol):
    def guardar(self, texto: str) -> None: ...


class AlmacenMemoria:
    def __init__(self):
        self.guardados = []

    def guardar(self, texto):
        self.guardados.append(texto)


class AlmacenConsola:
    def guardar(self, texto):
        print("   [almacén consola]", texto)


class Servicio:
    def __init__(self, almacen: Almacen):  # inyección por constructor
        self._almacen = almacen

    def cobrar(self):
        self._almacen.guardar("recibo")


if __name__ == "__main__":
    print("❌ Dependencia creada dentro de la clase:")
    try:
        ServicioMalo().cobrar()
    except OSError as error:
        print("   No se puede ni probar el servicio:", error)

    print("\n✅ Dependencia inyectada:")
    prueba = AlmacenMemoria()
    Servicio(prueba).cobrar()
    print("   En la prueba:", prueba.guardados)
    Servicio(AlmacenConsola()).cobrar()
    print("   Cambiar de almacén = cambiar UNA línea donde se arma el sistema, no el servicio.")
