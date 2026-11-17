"""Alfabeto y utilidades compartidas por todos los cifrados."""
import unicodedata

# Alfabeto español de 27 letras, en el mismo orden usado en la clave Gato/Vieja
ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
INDICE = {letra: i for i, letra in enumerate(ALFABETO)}

PUNTUACION_PERMITIDA = " .,;:!?¡¿-'/()\n0123456789"


def normalizar(texto: str) -> str:
    """Mayúsculas, sin acentos (pero conservando la Ñ), y solo caracteres soportados."""
    texto = texto.upper()
    salida = []
    for ch in texto:
        if ch == "Ñ":
            salida.append(ch)
            continue
        descompuesto = unicodedata.normalize("NFD", ch)
        base = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
        salida.append(base)
    texto = "".join(salida)
    return "".join(ch for ch in texto if ch in ALFABETO or ch in PUNTUACION_PERMITIDA)


def es_letra(ch: str) -> bool:
    return ch in INDICE
