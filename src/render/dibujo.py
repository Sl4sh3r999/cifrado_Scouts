"""Compositor: distribuye tokens cifrados en líneas y los dibuja sobre cualquier
backend que implemente la interfaz `Dibujante` (tkinter o PDF)."""
from dataclasses import dataclass, field


class Dibujante:
    """Interfaz mínima. Coordenadas con origen arriba-izquierda, y hacia abajo."""

    def linea(self, x1, y1, x2, y2, grosor=1.5): ...
    def punto(self, x, y, radio): ...
    def texto(self, x, y, txt, tam, negrita=False): ...   # anclado arriba-izquierda
    def ancho_texto(self, txt, tam, negrita=False) -> float: ...
    def alto_texto(self, tam) -> float: ...


@dataclass
class Estilo:
    tam_texto: float = 16
    tam_glifo: float = 24
    sep: float = 5
    sep_glifo: float = 11
    espacio_palabra: float = 18
    interlineado: float = 14

    @property
    def alto_glifo(self):
        return self.tam_glifo * 1.05

    @property
    def alto_linea(self):
        return max(self.alto_glifo, self.tam_texto * 1.3)


@dataclass
class Item:
    token: object
    x: float
    ancho: float


@dataclass
class Linea:
    items: list = field(default_factory=list)
    ancho: float = 0


def _ancho_token(dib, tok, est):
    if tok.tipo == "glifo":
        return est.tam_glifo
    return dib.ancho_texto(tok.valor, est.tam_texto)


ESPACIADOS = {"radiofonico"}


def usa_barra(tok):
    """Cifrados cuyo espacio entre palabras se marca con '/'."""
    return tok.tipo == "glifo" or tok.cifrado in ESPACIADOS


def _separador(prev, tok, est):
    """Hueco (y texto opcional) entre dos tokens consecutivos dentro de una palabra."""
    if prev is None:
        return 0, None
    if prev.tipo == "texto" and tok.tipo == "texto":
        if prev.cifrado == "numerico" and tok.cifrado == "numerico":
            return est.sep, "-"
        if prev.cifrado == tok.cifrado:
            return (est.sep * 2 if tok.cifrado in ESPACIADOS else 0), None
        return est.sep * 2, None
    if prev.tipo == "glifo" and tok.tipo == "glifo":
        return est.sep_glifo, None
    return est.sep * 2, None


def _palabras(tokens):
    actual = []
    for tok in tokens:
        if tok.tipo in ("espacio", "salto"):
            if actual:
                yield actual
                actual = []
            yield [tok]
        else:
            actual.append(tok)
    if actual:
        yield actual


def distribuir(dib, tokens, ancho_max, est: Estilo) -> list[Linea]:
    lineas = [Linea()]

    def nueva_linea():
        lineas.append(Linea())

    palabras = list(_palabras(tokens))
    for i, palabra in enumerate(palabras):
        if palabra[0].tipo == "salto":
            nueva_linea()
            continue
        if palabra[0].tipo == "espacio":
            linea = lineas[-1]
            if not linea.items:
                continue
            junto_a_glifo = (i > 0 and usa_barra(palabras[i - 1][-1])) or \
                            (i + 1 < len(palabras) and usa_barra(palabras[i + 1][0]))
            if junto_a_glifo:
                w = dib.ancho_texto("/", est.tam_texto)
                linea.ancho += est.sep * 2
                linea.items.append(Item(_Sep("/"), linea.ancho, w))
                linea.ancho += w + est.sep * 2
            else:
                linea.ancho += est.espacio_palabra
            continue

        piezas, prev = [], None
        for tok in palabra:
            items, x = [], 0.0
            hueco, sepTxt = _separador(prev, tok, est)
            if sepTxt:
                w = dib.ancho_texto(sepTxt, est.tam_texto)
                items.append(Item(_Sep(sepTxt), x + hueco / 2, w))
                x += hueco / 2 + w + hueco / 2
            else:
                x += hueco
            w = _ancho_token(dib, tok, est)
            items.append(Item(tok, x, w))
            piezas.append((items, x + w, hueco))
            prev = tok

        total = sum(p[1] for p in piezas)
        linea = lineas[-1]
        if linea.items and linea.ancho + total > ancho_max:
            nueva_linea()
            linea = lineas[-1]
        partir = total > ancho_max
        for k, (items, ancho_p, hueco) in enumerate(piezas):
            if partir and k and linea.items and linea.ancho + ancho_p > ancho_max:
                nueva_linea()
                linea = lineas[-1]
                for it in items:
                    it.x -= hueco
                ancho_p -= hueco
            base = linea.ancho
            for it in items:
                it.x += base
            linea.items.extend(items)
            linea.ancho = base + ancho_p
    if lineas and not lineas[-1].items:
        lineas.pop()
    return lineas


class _Sep:
    tipo = "texto"
    cifrado = None

    def __init__(self, valor):
        self.valor = valor


def _dibujar_gajo(dib, g, x, y, s, grosor):
    """Siete cruces: chevron del gajo de la X con el número de la cruz dentro."""
    a, b, v = 0.06, 0.94, 0.5
    if g.lado == "arriba":      # ∨
        pts, centro = [(a, a), (v, b), (b, a)], (0.5, 0.33)
    elif g.lado == "abajo":     # ∧
        pts, centro = [(a, b), (v, a), (b, b)], (0.5, 0.67)
    elif g.lado == "izq":       # >
        pts, centro = [(a, a), (b, v), (a, b)], (0.33, 0.5)
    else:                       # <
        pts, centro = [(b, a), (a, v), (b, b)], (0.67, 0.5)
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        dib.linea(x + x1 * s, y + y1 * s, x + x2 * s, y + y2 * s, grosor)
    tam_txt = s * 0.4
    txt = str(g.numero)
    w, h = dib.ancho_texto(txt, tam_txt), dib.alto_texto(tam_txt)
    dib.texto(x + centro[0] * s - w / 2, y + centro[1] * s - h / 2, txt, tam_txt)


def dibujar_glifo(dib, g, x, y, tam, grosor=1.6):
    s = tam
    if hasattr(g, "lado"):
        _dibujar_gajo(dib, g, x, y, s, grosor)
        return
    if g.borde_sup:
        dib.linea(x, y, x + s, y, grosor)
    if g.borde_inf:
        dib.linea(x, y + s, x + s, y + s, grosor)
    if g.borde_izq:
        dib.linea(x, y, x, y + s, grosor)
    if g.borde_der:
        dib.linea(x + s, y, x + s, y + s, grosor)
    px = x + s * (0.22, 0.5, 0.78)[g.punto]
    dib.punto(px, y + s * 0.74, s * 0.08)


def dibujar_linea(dib, linea: Linea, x0, y, est: Estilo):
    alto_txt = dib.alto_texto(est.tam_texto)
    y_txt = y + (est.tam_glifo - alto_txt) / 2
    for it in linea.items:
        tok = it.token
        if tok.tipo == "glifo":
            dibujar_glifo(dib, tok.valor, x0 + it.x, y, est.tam_glifo)
        else:
            dib.texto(x0 + it.x, y_txt, tok.valor, est.tam_texto)
