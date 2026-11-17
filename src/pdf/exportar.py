"""Generación del PDF imprimible."""
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter
from render.pdf_drawer import PdfDibujante
from render.documento import componer_documento


def generar_pdf(ruta, texto, tramos, incluir_leyenda=True, titulo=""):
    c = rl_canvas.Canvas(ruta, pagesize=letter)
    c.setTitle(titulo or "Mensaje cifrado")
    ancho, alto = letter
    componer_documento(PdfDibujante(c, alto), ancho, alto, c.showPage,
                       texto, tramos, incluir_leyenda, titulo)
    c.save()
