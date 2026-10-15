"""Los ejemplos correcto/incorrecto se ejecutan sin errores (son material de clase)."""

import subprocess
import sys
from pathlib import Path

import pytest

EJEMPLOS = sorted((Path(__file__).parent.parent / "ejemplos").glob("ejemplo_*.py"))


@pytest.mark.parametrize("ruta", EJEMPLOS, ids=lambda r: r.name)
def test_ejemplo_se_ejecuta(ruta):
    resultado = subprocess.run([sys.executable, str(ruta)], capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stderr
    assert "✅" in resultado.stdout


def test_hay_siete_ejemplos():
    assert len(EJEMPLOS) == 7
