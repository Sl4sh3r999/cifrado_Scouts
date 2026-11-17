"""Clave Siete Cruces: 7 cruces en X, cada una con 4 gajos (arriba, derecha, abajo, izquierda).

    cruz 1: A D B C   (arriba, izquierda, derecha, abajo)   cruz 5: P S Q R
    cruz 2: E H F G                                         cruz 6: T W U V
    cruz 3: I L J K                                         cruz 7: X . Y Z
    cruz 4: M O N Ñ

El símbolo de una letra es el gajo de la X donde está (un chevron) con el
número de la cruz dentro.
"""
from dataclasses import dataclass
from .base import ALFABETO, INDICE

ID = "sietecruces"
NOMBRE = "Siete cruces"

# Orden dentro de cada cruz: arriba, derecha, abajo, izquierda (sentido horario)
LADOS = ("arriba", "der", "abajo", "izq")
_ORDEN_CRUCES = [
    "ABCD", "EFGH", "IJKL", "MNÑO", "PQRS", "TUVW", "XYZ",
]


@dataclass(frozen=True)
class Glifo7:
    lado: str   # "arriba" | "der" | "abajo" | "izq"
    numero: int  # 1..7


_GLIFOS = {}
for _n, _letras in enumerate(_ORDEN_CRUCES, start=1):
    for _letra, _lado in zip(_letras, LADOS):
        _GLIFOS[_letra] = Glifo7(_lado, _n)


def cifrar_letra(ch: str) -> Glifo7:
    return _GLIFOS[ch]


_SIMBOLOS = {"arriba": "∨", "abajo": "∧", "izq": ">", "der": "<"}


def a_texto(g: Glifo7) -> str:
    return f"{_SIMBOLOS[g.lado]}{g.numero}"


def leyenda_filas():
    return [(letra, _GLIFOS[letra]) for letra in ALFABETO]
