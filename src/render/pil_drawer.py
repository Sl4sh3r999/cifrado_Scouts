"""Backend de dibujo sobre una imagen PIL (para copiar el mensaje como imagen)."""
import os
from PIL import Image, ImageDraw, ImageFont
from .dibujo import Dibujante, Estilo, distribuir, dibujar_linea

_FUENTES = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def _cargar(archivo, tam):
    try:
        return ImageFont.truetype(os.path.join(_FUENTES, archivo), max(1, int(round(tam))))
    except OSError:
        return ImageFont.load_default()


class PilDibujante(Dibujante):
    def __init__(self, imagen, escala):
        self.img = imagen
        self.d = ImageDraw.Draw(imagen)
        self.k = escala
        self._f = {}

    def _fuente(self, tam, negrita):
        clave = (round(tam * self.k * 10), negrita)
        if clave not in self._f:
            self._f[clave] = _cargar("arialbd.ttf" if negrita else "arial.ttf", tam * self.k)
        return self._f[clave]

    def linea(self, x1, y1, x2, y2, grosor=1.5):
        k = self.k
        self.d.line([(x1 * k, y1 * k), (x2 * k, y2 * k)], fill="black", width=max(1, round(grosor * k)))

    def punto(self, x, y, radio):
        k = self.k
        self.d.ellipse([(x - radio) * k, (y - radio) * k, (x + radio) * k, (y + radio) * k], fill="black")

    def texto(self, x, y, txt, tam, negrita=False):
        self.d.text((x * self.k, y * self.k), txt, fill="black", font=self._fuente(tam, negrita), anchor="la")

    def ancho_texto(self, txt, tam, negrita=False):
        return self._fuente(tam, negrita).getlength(txt) / self.k

    def alto_texto(self, tam):
        return tam * 1.2


def renderizar_mensaje(tokens, ancho=560, margen=16, escala=3):
    est = Estilo(tam_texto=18, tam_glifo=26)
    medidor = PilDibujante(Image.new("RGB", (1, 1)), escala)
    lineas = distribuir(medidor, tokens, ancho - 2 * margen, est)
    alto = int(2 * margen + max(1, len(lineas)) * (est.alto_linea + est.interlineado))
    img = Image.new("RGB", (ancho * escala, alto * escala), "white")
    dib = PilDibujante(img, escala)
    y = margen
    for ln in lineas:
        dibujar_linea(dib, ln, margen, y, est)
        y += est.alto_linea + est.interlineado
    return img
