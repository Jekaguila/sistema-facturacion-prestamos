"""EJEMPLO 1 · Herencia mal usada (INCORRECTO) frente a composición (CORRECTO).

Prueba rápida del tema 4.9:  ¿«X es un Y»  o  «X tiene un Y»?
Ejecutar:  python ejemplos/ejemplo_01_herencia_mal_usada.py
"""


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: Pila hereda de list solo para «reutilizar» append/pop
# ---------------------------------------------------------------------------
class PilaMala(list):
    def apilar(self, x):
        self.append(x)

    def desapilar(self):
        return self.pop()


# ✅ CORRECTO: la Pila TIENE una lista y expone solo lo que una pila permite
class Pila:
    def __init__(self):
        self._elementos = []  # detalle interno, oculto

    def apilar(self, x):
        self._elementos.append(x)

    def desapilar(self):
        if not self._elementos:
            raise IndexError("La pila está vacía")
        return self._elementos.pop()

    def __len__(self):
        return len(self._elementos)


# ---------------------------------------------------------------------------
# ❌ INCORRECTO: «un Préstamo es un Cliente» (relación ES-UN falsa)
# ✅ CORRECTO:   «un Préstamo tiene un Cliente» (asociación)
# ---------------------------------------------------------------------------
class ClienteMalo:
    def __init__(self, nombre):
        self.nombre = nombre


class PrestamoMalo(ClienteMalo):  # ¿Un préstamo es una persona? No.
    def __init__(self, nombre, monto):
        super().__init__(nombre)
        self.monto = monto


class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre


class Prestamo:
    def __init__(self, cliente, monto):
        self.cliente = cliente  # TIENE-UN
        self.monto = monto


if __name__ == "__main__":
    print("--- ❌ Pila que hereda de list ---")
    mala = PilaMala()
    mala.apilar(1)
    mala.apilar(2)
    mala.insert(0, 99)  # ¡rompe la regla LIFO! list expone TODO
    mala.sort()  # y también esto
    print("Contenido tras insert/sort:", list(mala), "← ya no es una pila")

    print("\n--- ✅ Pila con composición ---")
    buena = Pila()
    buena.apilar(1)
    buena.apilar(2)
    print("¿Tiene insert()?", hasattr(buena, "insert"))
    print("Desapila:", buena.desapilar(), "→ solo se puede operar como pila")

    print("\n--- ❌ Préstamo que hereda de Cliente ---")
    pm = PrestamoMalo("Ana", 500)
    print("isinstance(pm, ClienteMalo):", isinstance(pm, ClienteMalo), "← absurdo")

    print("\n--- ✅ Préstamo que tiene un Cliente ---")
    p = Prestamo(Cliente("Ana"), 500)
    print("Titular:", p.cliente.nombre, "| ¿es un Cliente?", isinstance(p, Cliente))
