"""Cifrado Murciélago: las letras de la palabra MURCIELAGO se sustituyen por su
posición (0-9) dentro de esa palabra. El resto de las letras se dejan igual.

Ejemplo verificado: SILENCIO -> S465N349, BANDADA -> B7ND7D7
"""
CLAVE = "MURCIELAGO"
_MAPA = {letra: str(i) for i, letra in enumerate(CLAVE)}

ID = "murcielago"
NOMBRE = "Murciélago"


def cifrar_letra(ch: str) -> str:
    return _MAPA.get(ch, ch)


def leyenda_filas():
    from .base import ALFABETO
    return [(letra, _MAPA.get(letra, letra)) for letra in ALFABETO]
