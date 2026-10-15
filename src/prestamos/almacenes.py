"""Dónde se guardan los datos: contratos y dos implementaciones.

Inversión de Dependencias (DIP): ``ServicioPrestamos`` depende de estos CONTRATOS
(Protocol), no de ``RepositorioMemoria`` ni de la carpeta ``recibos/``. En las pruebas
se usan las versiones en memoria; en producción, las de archivo (o una base de datos).
"""

from pathlib import Path
from typing import Protocol

from .excepciones import NoEncontradoError
from .prestamo import Prestamo


class RepositorioPrestamos(Protocol):
    def guardar(self, prestamo: Prestamo) -> None: ...
    def obtener(self, codigo: str) -> Prestamo: ...
    def listar(self) -> list[Prestamo]: ...


class AlmacenDocumentos(Protocol):
    def guardar(self, nombre: str, contenido: str) -> str: ...


class RepositorioMemoria:
    def __init__(self):
        self._datos: dict[str, Prestamo] = {}

    def guardar(self, prestamo: Prestamo) -> None:
        self._datos[prestamo.codigo] = prestamo

    def obtener(self, codigo: str) -> Prestamo:
        try:
            return self._datos[codigo]
        except KeyError:
            raise NoEncontradoError(f"No existe el préstamo {codigo!r}") from None

    def listar(self) -> list[Prestamo]:
        return list(self._datos.values())


class AlmacenMemoria:
    """Guarda documentos en un diccionario (ideal para pruebas)."""

    def __init__(self):
        self.documentos: dict[str, str] = {}

    def guardar(self, nombre: str, contenido: str) -> str:
        self.documentos[nombre] = contenido
        return nombre


class AlmacenCarpeta:
    """Guarda cada documento como archivo dentro de una carpeta."""

    def __init__(self, carpeta: str | Path):
        self._carpeta = Path(carpeta)
        self._carpeta.mkdir(parents=True, exist_ok=True)

    def guardar(self, nombre: str, contenido: str) -> str:
        ruta = self._carpeta / nombre
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return str(ruta)
