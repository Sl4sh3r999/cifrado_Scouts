"""Registro de cifrados disponibles y construcción de tramos (segmentos)."""
from dataclasses import dataclass
from . import numerico, inversa, murcielago, gato, sietecruces, cenitpolar, radiofonico
from .base import normalizar, es_letra

CIFRADOS = {
    numerico.ID: numerico,
    gato.ID: gato,
    inversa.ID: inversa,
    murcielago.ID: murcielago,
    sietecruces.ID: sietecruces,
    cenitpolar.ID: cenitpolar,
    radiofonico.ID: radiofonico,
}
ORDEN = [numerico.ID, gato.ID, inversa.ID, murcielago.ID, sietecruces.ID, cenitpolar.ID, radiofonico.ID]
SIN_CIFRAR = "ninguno"


def nombre(cifrado_id: str) -> str:
    if cifrado_id == SIN_CIFRAR:
        return "Sin cifrar"
    return CIFRADOS[cifrado_id].NOMBRE


@dataclass
class Tramo:
    cifrado: str
    longitud: int


@dataclass
class Token:
    tipo: str      # "texto" | "glifo" | "espacio" | "salto"
    valor: object  # str para texto, Glifo para glifo
    cifrado: str | None = None


def usa_barra(tok: Token) -> bool:
    return tok.tipo == "glifo" or tok.cifrado == radiofonico.ID


def a_texto_plano(tokens: list[Token]) -> str:
    """Texto copiable del mensaje cifrado (los cifrados gráficos usan símbolos Unicode)."""
    salida: list[str] = []
    prev: Token | None = None
    espera_sep = False
    for tok in tokens:
        if tok.tipo == "salto":
            salida.append("\n")
            prev, espera_sep = None, False
        elif tok.tipo == "espacio":
            espera_sep = True
        else:
            valor = CIFRADOS[tok.cifrado].a_texto(tok.valor) if tok.tipo == "glifo" else tok.valor
            if espera_sep and prev is not None:
                con_barra = usa_barra(prev) or usa_barra(tok)
                salida.append(" / " if con_barra else " ")
            elif prev is not None:
                if prev.cifrado == "numerico" and tok.cifrado == "numerico":
                    salida.append("-")
                elif prev.tipo == "glifo" or tok.tipo == "glifo":
                    salida.append(" ")
                elif prev.cifrado == tok.cifrado == radiofonico.ID:
                    salida.append(" ")
                elif prev.cifrado != tok.cifrado:
                    salida.append(" ")
            salida.append(valor)
            prev, espera_sep = tok, False
    return "".join(salida)


def contar_letras(texto: str) -> int:
    return sum(1 for ch in normalizar(texto) if es_letra(ch))


def asignacion(tramos: list[Tramo], total: int) -> list[str | None]:
    """Cifrado asignado a cada letra del mensaje (None = sin tramo)."""
    cola = [t.cifrado for t in tramos for _ in range(max(0, t.longitud))]
    return (cola + [None] * total)[:total]


def tramos_desde_asignacion(asig: list[str | None]) -> list[Tramo]:
    """Compacta una asignación por letra en tramos consecutivos.
    Los huecos intermedios se convierten en tramos 'Sin cifrar'; los finales se descartan."""
    while asig and asig[-1] is None:
        asig = asig[:-1]
    tramos: list[Tramo] = []
    for cid in asig:
        cid = cid or SIN_CIFRAR
        if tramos and tramos[-1].cifrado == cid:
            tramos[-1].longitud += 1
        else:
            tramos.append(Tramo(cid, 1))
    return tramos


def construir_tokens(texto: str, tramos: list[Tramo]) -> list[Token]:
    """Convierte el mensaje en tokens ya cifrados según la secuencia de tramos.

    Los tramos consumen únicamente letras; espacios y puntuación pasan sin
    cifrar. Las letras no cubiertas por ningún tramo quedan sin cifrar.
    """
    texto = normalizar(texto)
    cola = [t.cifrado for t in tramos for _ in range(max(0, t.longitud))]
    tokens: list[Token] = []
    for ch in texto:
        if ch == "\n":
            tokens.append(Token("salto", None))
        elif ch == " ":
            tokens.append(Token("espacio", None))
        elif es_letra(ch):
            cifrado_id = cola.pop(0) if cola else SIN_CIFRAR
            if cifrado_id == SIN_CIFRAR:
                tokens.append(Token("texto", ch))
                continue
            salida = CIFRADOS[cifrado_id].cifrar_letra(ch)
            tipo = "texto" if isinstance(salida, str) else "glifo"
            tokens.append(Token(tipo, salida, cifrado_id))
        else:
            tokens.append(Token("texto", ch))
    return tokens
