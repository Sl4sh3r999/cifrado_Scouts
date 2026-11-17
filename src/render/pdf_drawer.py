"""Backend de dibujo sobre un canvas de reportlab (eje Y invertido)."""
from reportlab.pdfbase import pdfmetrics
from .dibujo import Dibujante

FUENTE = "Helvetica"
FUENTE_NEGRITA = "Helvetica-Bold"


class PdfDibujante(Dibujante):
    def __init__(self, canvas, alto_pagina):
        self.c = canvas
        self.h = alto_pagina

    def _y(self, y):
        return self.h - y

    def linea(self, x1, y1, x2, y2, grosor=1.5):
        self.c.setLineWidth(grosor)
        self.c.setLineCap(1)
        self.c.line(x1, self._y(y1), x2, self._y(y2))

    def punto(self, x, y, radio):
        self.c.circle(x, self._y(y), radio, stroke=0, fill=1)

    def texto(self, x, y, txt, tam, negrita=False):
        fuente = FUENTE_NEGRITA if negrita else FUENTE
        self.c.setFont(fuente, tam)
        self.c.drawString(x, self._y(y + tam * 0.9), txt)

    def ancho_texto(self, txt, tam, negrita=False):
        return pdfmetrics.stringWidth(txt, FUENTE_NEGRITA if negrita else FUENTE, tam)

    def alto_texto(self, tam):
        return tam * 1.2
