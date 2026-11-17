"""Backend de dibujo sobre un tkinter.Canvas."""
import tkinter.font as tkfont
from .dibujo import Dibujante

FUENTE = "Segoe UI"


class TkDibujante(Dibujante):
    def __init__(self, canvas, color="#111111"):
        self.c = canvas
        self.color = color
        self._fuentes = {}

    def _fuente(self, tam, negrita=False):
        clave = (round(tam), negrita)
        if clave not in self._fuentes:
            self._fuentes[clave] = tkfont.Font(
                family=FUENTE, size=-int(round(tam)),
                weight="bold" if negrita else "normal")
        return self._fuentes[clave]

    def linea(self, x1, y1, x2, y2, grosor=1.5):
        self.c.create_line(x1, y1, x2, y2, width=grosor, fill=self.color, capstyle="round")

    def punto(self, x, y, radio):
        self.c.create_oval(x - radio, y - radio, x + radio, y + radio,
                           fill=self.color, outline=self.color)

    def texto(self, x, y, txt, tam, negrita=False):
        self.c.create_text(x, y, text=txt, anchor="nw",
                           font=self._fuente(tam, negrita), fill=self.color)

    def ancho_texto(self, txt, tam, negrita=False):
        return self._fuente(tam, negrita).measure(txt)

    def alto_texto(self, tam):
        return self._fuente(tam).metrics("linespace")
