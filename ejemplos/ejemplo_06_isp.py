"""EJEMPLO 6 · I — Segregación de Interfaces (ISP).

«Ninguna clase debe depender de métodos que no usa.»
Ejecutar:  python ejemplos/ejemplo_06_isp.py
"""

from abc import ABC, abstractmethod
from typing import Protocol


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: una interfaz «gorda» obliga a implementar lo que no se necesita
# ---------------------------------------------------------------------------
class DocumentoMalo(ABC):
    @abstractmethod
    def imprimir(self): ...
    @abstractmethod
    def enviar_por_correo(self): ...
    @abstractmethod
    def firmar_digitalmente(self): ...


class ReciboSimpleMalo(DocumentoMalo):
    def imprimir(self):
        return "imprimiendo recibo"

    def enviar_por_correo(self):
        raise NotImplementedError("Este recibo no se envía")  # relleno inútil

    def firmar_digitalmente(self):
        raise NotImplementedError("Este recibo no se firma")  # relleno inútil


# ---------------------------------------------------------------------------
# ✅ CORRECTO: contratos pequeños; cada clase adopta solo los que necesita
# ---------------------------------------------------------------------------
class Imprimible(Protocol):
    def imprimir(self) -> str: ...


class Enviable(Protocol):
    def enviar_por_correo(self) -> str: ...


class ReciboSimple:  # solo es imprimible
    def imprimir(self):
        return "imprimiendo recibo"


class FacturaElectronica:  # imprimible y enviable
    def imprimir(self):
        return "imprimiendo factura"

    def enviar_por_correo(self):
        return "factura enviada"


def imprimir_todo(docs: list[Imprimible]):
    return [d.imprimir() for d in docs]


def notificar(docs: list[Enviable]):
    return [d.enviar_por_correo() for d in docs]


if __name__ == "__main__":
    print("❌ Interfaz gorda:")
    r = ReciboSimpleMalo()
    try:
        r.enviar_por_correo()
    except NotImplementedError as error:
        print("   ", error, "← método obligatorio que no tiene sentido aquí")

    print("\n✅ Interfaces pequeñas (Protocol):")
    print("  ", imprimir_todo([ReciboSimple(), FacturaElectronica()]))
    print("  ", notificar([FacturaElectronica()]))
    print("   ReciboSimple no se pasa a `notificar`: no tiene ese método ni se le exige.")
