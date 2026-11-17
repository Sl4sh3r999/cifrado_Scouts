"""Cifrado del Gato (Clave Vieja): pigpen sobre un meta-grid 3x3.

El alfabeto de 27 letras se agrupa de 3 en 3 en 9 "celdas grandes" dispuestas
en cuadrícula 3x3:

    A B C | D E F | G H I
    ------+-------+------
    J K L | M N Ñ | O P Q
    ------+-------+------
    R S T | U V W | X Y Z

El símbolo de cada letra es el contorno de su celda (solo se dibujan los
lados internos de la cuadrícula que tocan esa celda) más un punto debajo,
colocado a la izquierda / centro / derecha según la letra sea la 1a, 2a o
3a del grupo.
"""
from dataclasses import dataclass
from .base import ALFABETO, INDICE

ID = "gato"
NOMBRE = "Gato (Clave Vieja)"


@dataclass(frozen=True)
class Glifo:
    borde_izq: bool
    borde_der: bool
    borde_sup: bool
    borde_inf: bool
    punto: int  # 0=izquierda, 1=centro, 2=derecha


def _glifo_para_indice(i: int) -> Glifo:
    celda = i // 3
    punto = i % 3
    fila, col = divmod(celda, 3)
    return Glifo(
        borde_izq=col > 0,
        borde_der=col < 2,
        borde_sup=fila > 0,
        borde_inf=fila < 2,
        punto=punto,
    )


def cifrar_letra(ch: str) -> Glifo:
    return _glifo_para_indice(INDICE[ch])


_FORMAS = {
    (False, True, False, True): "┘",    # der + inf
    (True, False, False, True): "└",    # izq + inf
    (True, True, False, True): "⊔",
    (False, True, True, True): "⊐",
    (True, True, True, True): "□",
    (True, False, True, True): "⊏",
    (False, True, True, False): "┐",
    (True, False, True, False): "┌",
    (True, True, True, False): "⊓",
}


def a_texto(g: Glifo) -> str:
    """Forma de la celda (caracteres de dibujo) + 1, 2 o 3 puntos según la posición del punto."""
    forma = _FORMAS[(g.borde_izq, g.borde_der, g.borde_sup, g.borde_inf)]
    return forma + "•" * (g.punto + 1)


def leyenda_filas():
    return [(letra, _glifo_para_indice(i)) for i, letra in enumerate(ALFABETO)]
