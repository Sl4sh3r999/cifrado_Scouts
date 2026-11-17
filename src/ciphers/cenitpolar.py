"""Clave Cenit Polar: cada letra de CENIT se cambia por la de POLAR que está debajo
(y viceversa). Las demás letras no cambian.

Ejemplo verificado: CREATIVIDAD -> PTOIRAVADID
"""
ARRIBA = "CENIT"
ABAJO = "POLAR"
_MAPA = {}
for _a, _b in zip(ARRIBA, ABAJO):
    _MAPA[_a] = _b
    _MAPA[_b] = _a

ID = "cenitpolar"
NOMBRE = "Cenit Polar"


def cifrar_letra(ch: str) -> str:
    return _MAPA.get(ch, ch)


def leyenda_filas():
    from .base import ALFABETO
    return [(letra, _MAPA.get(letra, letra)) for letra in ALFABETO]
