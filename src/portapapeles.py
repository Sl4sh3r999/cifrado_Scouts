"""Copiar al portapapeles de Windows (texto o imagen)."""
import io
import win32clipboard
import win32con


def copiar_texto(texto: str):
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, texto)
    finally:
        win32clipboard.CloseClipboard()


def copiar_imagen(imagen):
    """imagen: PIL.Image. Se copia como DIB (se puede pegar en WhatsApp, Word, etc.)."""
    salida = io.BytesIO()
    imagen.convert("RGB").save(salida, "BMP")
    datos = salida.getvalue()[14:]
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_DIB, datos)
    finally:
        win32clipboard.CloseClipboard()
