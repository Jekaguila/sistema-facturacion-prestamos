"""Ejecuta los siete ejemplos en orden (útil para clase y para pruebas)."""

import pathlib
import subprocess
import sys

carpeta = pathlib.Path(__file__).parent
for ruta in sorted(carpeta.glob("ejemplo_*.py")):
    print("=" * 72, f"\n{ruta.name}\n" + "=" * 72)
    resultado = subprocess.run(
        [sys.executable, str(ruta)], capture_output=True, text=True, check=False
    )
    print(resultado.stdout, resultado.stderr)
    if resultado.returncode:
        sys.exit(f"FALLÓ {ruta.name}")
