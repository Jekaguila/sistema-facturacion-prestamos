"""Demostración por consola: préstamo con tasa que cambia y recibos por cada cuota.

Ejecutar:   python main.py
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from prestamos import (  # noqa: E402
    AlmacenCarpeta,
    Cliente,
    FrancesCuotaFija,
    GeneradorRecibos,
    RepositorioMemoria,
    SecuenciaNumeracion,
    ServicioPrestamos,
    obtener_formateador,
)
from prestamos.dinero import fmt  # noqa: E402
from prestamos.formatos import factura_a_texto  # noqa: E402


def main() -> None:
    # --- composición del sistema: aquí (y solo aquí) se eligen las piezas concretas ---
    servicio = ServicioPrestamos(
        repositorio=RepositorioMemoria(),
        generador=GeneradorRecibos(SecuenciaNumeracion("R")),
        almacen=AlmacenCarpeta(Path(__file__).parent / "recibos_generados"),
        formateador=obtener_formateador("txt"),
        numeracion_facturas=SecuenciaNumeracion("F"),
    )

    cliente = Cliente("04567891-2", "María Elena Contreras")
    prestamo = servicio.crear_prestamo(
        "P-001", cliente, 1200, 12, date(2026, 1, 15), 12, FrancesCuotaFija()
    )
    factura = servicio.facturar_cargos(prestamo, date(2026, 1, 15))
    print(factura_a_texto(factura), "\n")

    for fecha in (date(2026, 2, 15), date(2026, 3, 15), date(2026, 4, 15)):
        servicio.cobrar_cuota("P-001", fecha)

    # La tasa sube al 18 % anual a partir del 1 de mayo: la cuota 4 ya la usa.
    servicio.cambiar_tasa("P-001", date(2026, 5, 1), 18)
    recibo, ruta = servicio.cobrar_cuota("P-001", date(2026, 5, 15))
    print(obtener_formateador("txt").formatear(recibo), f"\n(guardado en {ruta})\n")

    # Cuota 5 pagada con 12 días de atraso -> mora y factura del cargo.
    recibo, _ = servicio.cobrar_cuota("P-001", date(2026, 6, 27))
    print(obtener_formateador("txt").formatear(recibo))
    factura = servicio.facturar_cargos(prestamo, date(2026, 6, 27), recibo.pago)
    print(factura_a_texto(factura), "\n")

    print("Proyección de las cuotas que faltan (con las tasas ya registradas):")
    for fila in prestamo.proyeccion():
        print(
            f"  #{fila.numero_cuota:>2}  {fila.fecha_vencimiento}  {fila.tasa_anual:>5}%  "
            f"cuota {fmt(fila.cuota):>9}  saldo {fmt(fila.saldo_final):>10}"
        )
    print()
    print("\n".join(servicio.estado_de_cuenta("P-001")))


if __name__ == "__main__":
    main()
