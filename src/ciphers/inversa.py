"""Cifrado inversa (Atbash): cada letra se sustituye por su opuesta en el alfabeto (A<->Z, B<->Y...)."""
from .base import ALFABETO, INDICE

ID = "inversa"
NOMBRE = "Inversa (espejo)"

_N = len(ALFABETO)


def cifrar_letra(ch: str) -> str:
    return ALFABETO[_N - 1 - INDICE[ch]]


def leyenda_filas():
    return [(letra, ALFABETO[_N - 1 - i]) for i, letra in enumerate(ALFABETO)]
