"""Impresión directa a una impresora de Windows sin archivo intermedio."""
import win32print
import win32ui
import win32con
from render.gdi_drawer import GdiDibujante
from render.documento import componer_documento


def listar_impresoras():
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    nombres = [p[2] for p in win32print.EnumPrinters(flags)]
    try:
        predeterminada = win32print.GetDefaultPrinter()
    except Exception:
        predeterminada = nombres[0] if nombres else ""
    return nombres, predeterminada


def imprimir(texto, tramos, incluir_leyenda=True, titulo="", impresora=None, archivo_salida=None):
    impresora = impresora or win32print.GetDefaultPrinter()
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(impresora)
    try:
        dpi_x = dc.GetDeviceCaps(win32con.LOGPIXELSX)
        dpi_y = dc.GetDeviceCaps(win32con.LOGPIXELSY)
        ancho = dc.GetDeviceCaps(win32con.HORZRES) * 72 / dpi_x
        alto = dc.GetDeviceCaps(win32con.VERTRES) * 72 / dpi_y

        nombre_doc = titulo or "Mensaje cifrado"
        if archivo_salida:
            dc.StartDoc(nombre_doc, archivo_salida)
        else:
            dc.StartDoc(nombre_doc)
        dc.StartPage()

        def nueva_pagina():
            dc.EndPage()
            dc.StartPage()

        try:
            componer_documento(GdiDibujante(dc, dpi_x, dpi_y), ancho, alto, nueva_pagina,
                               texto, tramos, incluir_leyenda, titulo)
            dc.EndPage()
            dc.EndDoc()
        except Exception:
            dc.AbortDoc()
            raise
    finally:
        dc.DeleteDC()
