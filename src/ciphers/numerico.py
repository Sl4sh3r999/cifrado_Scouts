"""Cifrado numérico: cada letra se sustituye por su posición en el alfabeto (A=1 ... Z=27)."""
from .base import INDICE

ID = "numerico"
NOMBRE = "Numérico"


def cifrar_letra(ch: str) -> str:
    return str(INDICE[ch] + 1)


def leyenda_filas():
    """Filas (letra, valor) para la tabla de referencia."""
    from .base import ALFABETO
    return [(letra, str(i + 1)) for i, letra in enumerate(ALFABETO)]
