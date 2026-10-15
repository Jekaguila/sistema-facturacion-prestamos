"""Cliente del préstamo."""

from .excepciones import DatoInvalidoError


class Cliente:
    """Persona que recibe el préstamo. Se identifica por su documento."""

    def __init__(self, documento: str, nombre: str, correo: str = ""):
        if not documento or not documento.strip():
            raise DatoInvalidoError("El documento es obligatorio")
        if not nombre or not nombre.strip():
            raise DatoInvalidoError("El nombre es obligatorio")
        self._documento = documento.strip()  # privado por convención: es la identidad
        self.nombre = nombre.strip()
        self.correo = correo.strip()

    @property
    def documento(self) -> str:
        return self._documento

    def __eq__(self, otro):
        if not isinstance(otro, Cliente):
            return NotImplemented
        return self._documento == otro._documento

    def __hash__(self):
        return hash(self._documento)

    def __repr__(self):
        return f"Cliente({self._documento!r}, {self.nombre!r})"
