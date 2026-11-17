"""Alfabeto radiofónico: cada letra se sustituye por su palabra (A=Alpha ... Z=Zulu).
La Ñ (que no tiene palabra oficial) se dice "Eñe"."""
from .base import ALFABETO

ID = "radiofonico"
NOMBRE = "Radiofónico"

_PALABRAS = {
    "A": "Alpha", "B": "Bravo", "C": "Charlie", "D": "Delta", "E": "Echo",
    "F": "Foxtrot", "G": "Golf", "H": "Hotel", "I": "India", "J": "Juliett",
    "K": "Kilo", "L": "Lima", "M": "Mike", "N": "November", "Ñ": "Eñe",
    "O": "Oscar", "P": "Papa", "Q": "Quebec", "R": "Romeo", "S": "Sierra",
    "T": "Tango", "U": "Uniform", "V": "Victor", "W": "Whiskey", "X": "X-ray",
    "Y": "Yankee", "Z": "Zulu",
}


def cifrar_letra(ch: str) -> str:
    return _PALABRAS[ch]


def leyenda_filas():
    return [(letra, _PALABRAS[letra]) for letra in ALFABETO]
