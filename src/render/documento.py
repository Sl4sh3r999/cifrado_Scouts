"""Flujo de documento paginado: mensaje cifrado + leyenda opcional.
Independiente del backend (PDF o impresora GDI)."""
from ciphers.registro import construir_tokens, CIFRADOS, ORDEN, nombre
from ciphers import gato, murcielago, sietecruces
from .dibujo import Estilo, distribuir, dibujar_linea, dibujar_glifo

DESCRIPCIONES = {
    "numerico": "Cada letra se sustituye por su posición en el alfabeto (A=1 ... Z=27). "
                "Los números de una misma palabra van separados por guiones.",
    "inversa": "Cada letra se sustituye por su opuesta en el alfabeto (A<->Z, B<->Y, C<->X...).",
    "murcielago": "Las letras de la palabra MURCIELAGO se sustituyen por su posición (0-9). "
                  "Las demás letras se escriben tal cual.",
    "gato": "Se dibuja el contorno de la celda donde está la letra, más un punto debajo "
            "(izquierda, centro o derecha) según sea la 1a, 2a o 3a letra de esa celda.",
    "radiofonico": "Cada letra se sustituye por su palabra del alfabeto radiofónico (A = Alpha, "
                   "B = Bravo ...). Las palabras de un mismo mensaje se separan con \"/\". "
                   "La Ñ se dice \"Eñe\".",
    "cenitpolar": "Cada letra de CENIT se reemplaza por la de POLAR que está debajo, y viceversa "
                  "(C<->P, E<->O, N<->L, I<->A, T<->R). Las demás letras no cambian.",
    "sietecruces": "Hay 7 cruces en X numeradas del 1 al 7; cada una tiene 4 gajos (arriba, derecha, "
                   "abajo, izquierda). La letra se escribe con el gajo donde está (un chevron: "
                   "arriba, abajo, izquierda o derecha) y el número de su cruz dentro.",
}


class Documento:
    def __init__(self, dib, ancho, alto, margen, nueva_pagina):
        self.dib = dib
        self.w, self.h, self.m = ancho, alto, margen
        self._nueva = nueva_pagina
        self.y = margen

    @property
    def ancho_util(self):
        return self.w - 2 * self.m

    def salto_pagina(self):
        self._nueva()
        self.y = self.m

    def asegurar(self, alto):
        if self.y + alto > self.h - self.m:
            self.salto_pagina()

    def titulo(self, txt, tam=16):
        self.asegurar(tam * 2)
        self.dib.texto(self.m, self.y, txt, tam, negrita=True)
        self.y += tam * 1.8

    def parrafo(self, txt, tam=10):
        lineas, actual = [], ""
        for palabra in txt.split():
            prueba = f"{actual} {palabra}".strip()
            if actual and self.dib.ancho_texto(prueba, tam) > self.ancho_util:
                lineas.append(actual)
                actual = palabra
            else:
                actual = prueba
        if actual:
            lineas.append(actual)
        for l in lineas:
            self.asegurar(tam * 1.4)
            self.dib.texto(self.m, self.y, l, tam)
            self.y += tam * 1.4
        self.y += tam * 0.6

    def mensaje(self, tokens, est: Estilo):
        for ln in distribuir(self.dib, tokens, self.ancho_util, est):
            self.asegurar(est.alto_linea)
            dibujar_linea(self.dib, ln, self.m, self.y, est)
            self.y += est.alto_linea + est.interlineado

    def leyenda(self, usados):
        self.titulo("Leyenda de cifrados", 18)
        for cid in usados:
            self.titulo(nombre(cid), 13)
            self.parrafo(DESCRIPCIONES[cid])
            if cid == gato.ID:
                self._leyenda_glifos(gato.leyenda_filas(), 9, 3)
            elif cid == sietecruces.ID:
                self._leyenda_glifos(sietecruces.leyenda_filas(), 8, 4)
            elif cid == murcielago.ID:
                self._leyenda_murcielago()
            else:
                por_fila = 4 if cid == "radiofonico" else 9
                self._leyenda_tabla(CIFRADOS[cid].leyenda_filas(), por_fila)
            self.y += 12

    def _leyenda_tabla(self, filas, por_fila=9, tam=11):
        ancho = self.ancho_util / por_fila
        for i in range(0, len(filas), por_fila):
            self.asegurar(tam * 1.6)
            for j, (letra, val) in enumerate(filas[i:i + por_fila]):
                self.dib.texto(self.m + j * ancho, self.y, f"{letra} = {val}", tam)
            self.y += tam * 1.6

    def _leyenda_murcielago(self, tam=13):
        ancho = 28
        self.asegurar(tam * 3.2)
        for i, (letra, digito) in enumerate(zip(murcielago.CLAVE, "0123456789")):
            x = self.m + i * ancho
            self.dib.texto(x, self.y, letra, tam, negrita=True)
            self.dib.texto(x, self.y + tam * 1.4, digito, tam)
        self.y += tam * 3.2

    def _leyenda_glifos(self, filas, por_fila, grupo, tam_glifo=20, tam_letra=11):
        hueco_grupo = 10
        ancho_celda = (self.ancho_util - (por_fila // grupo) * hueco_grupo) / por_fila
        alto_fila = tam_letra * 1.4 + tam_glifo * 1.1 + 10
        for i in range(0, len(filas), por_fila):
            self.asegurar(alto_fila)
            for j, (letra, g) in enumerate(filas[i:i + por_fila]):
                x = self.m + j * ancho_celda + (j // grupo) * hueco_grupo + (ancho_celda - tam_glifo) / 2
                lw = self.dib.ancho_texto(letra, tam_letra, negrita=True)
                self.dib.texto(x + (tam_glifo - lw) / 2, self.y, letra, tam_letra, negrita=True)
                dibujar_glifo(self.dib, g, x, self.y + tam_letra * 1.4, tam_glifo)
            self.y += alto_fila


def cifrados_usados(tokens):
    return [cid for cid in ORDEN if any(t.cifrado == cid for t in tokens)]


def componer_documento(dib, ancho, alto, nueva_pagina, texto, tramos,
                       incluir_leyenda=True, titulo="", margen=56):
    doc = Documento(dib, ancho, alto, margen, nueva_pagina)
    if titulo:
        doc.titulo(titulo, 18)
        doc.y += 6
    tokens = construir_tokens(texto, tramos)
    doc.mensaje(tokens, Estilo())
    if incluir_leyenda:
        usados = cifrados_usados(tokens)
        if usados:
            doc.salto_pagina()
            doc.leyenda(usados)
