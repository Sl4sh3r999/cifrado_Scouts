"""Interfaz gráfica principal (tkinter)."""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ciphers.registro import (ORDEN, SIN_CIFRAR, nombre, Tramo, construir_tokens, contar_letras,
                              asignacion, tramos_desde_asignacion, a_texto_plano)
import portapapeles
from render.pil_drawer import renderizar_mensaje
from render.tk_drawer import TkDibujante
from render.dibujo import Estilo, distribuir, dibujar_linea
from pdf.exportar import generar_pdf

try:
    import impresion
except ImportError:
    impresion = None

IDS = ORDEN + [SIN_CIFRAR]
NOMBRES = [nombre(c) for c in IDS]
ID_POR_NOMBRE = dict(zip(NOMBRES, IDS))
COLORES = {
    "numerico": "#cfe3ff",
    "gato": "#ffd9a8",
    "inversa": "#cdf2c9",
    "murcielago": "#efcdf5",
    "sietecruces": "#fff0a0",
    "cenitpolar": "#b8ece8",
    "radiofonico": "#ffc9c9",
    SIN_CIFRAR: "#e6e6e6",
}
PLACEHOLDER_SEL = "Cifrar selección como…"


class FilaTramo(ttk.Frame):
    def __init__(self, master, indice, on_cambio, on_quitar, cifrado=ORDEN[0], longitud=5):
        super().__init__(master)
        self.var_cifrado = tk.StringVar(value=nombre(cifrado))
        self.var_longitud = tk.StringVar(value=str(longitud))
        self.etiqueta = ttk.Label(self, text=f"Tramo {indice}", width=9)
        self.etiqueta.pack(side="left")
        self.color = tk.Label(self, width=2, bg=COLORES[cifrado])
        self.color.pack(side="left", padx=(0, 4))
        ttk.Combobox(self, textvariable=self.var_cifrado, values=NOMBRES, exportselection=False,
                     state="readonly", width=18).pack(side="left", padx=4)
        ttk.Spinbox(self, from_=1, to=999, textvariable=self.var_longitud, width=6).pack(side="left", padx=4)
        ttk.Label(self, text="letras").pack(side="left")
        ttk.Button(self, text="Quitar", width=7, command=lambda: on_quitar(self)).pack(side="right")
        self.var_cifrado.trace_add("write", lambda *_: self._cambio_cifrado(on_cambio))
        self.var_longitud.trace_add("write", lambda *_: on_cambio())

    def _cambio_cifrado(self, on_cambio):
        self.color.config(bg=COLORES[ID_POR_NOMBRE[self.var_cifrado.get()]])
        on_cambio()

    def tramo(self) -> Tramo:
        try:
            longitud = max(0, int(self.var_longitud.get()))
        except ValueError:
            longitud = 0
        return Tramo(ID_POR_NOMBRE[self.var_cifrado.get()], longitud)

    def renumerar(self, indice):
        self.etiqueta.config(text=f"Tramo {indice}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codificador de mensajes")
        self.geometry("1050x700")
        self.minsize(860, 580)
        self.filas: list[FilaTramo] = []
        self._pendiente = None
        self._sel_rango = None
        self._construir()
        self.programar_actualizacion()
        self.bind("<Configure>", lambda e: self.programar_actualizacion())

    # ---------- construcción ----------
    def _construir(self):
        raiz = ttk.Frame(self, padding=10)
        raiz.pack(fill="both", expand=True)
        raiz.columnconfigure(1, weight=1)
        raiz.rowconfigure(0, weight=1)

        izq = ttk.Frame(raiz, width=400)
        izq.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        izq.grid_propagate(False)
        izq.rowconfigure(4, weight=1)
        izq.columnconfigure(0, weight=1)

        ttk.Label(izq, text="Mensaje", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.texto = tk.Text(izq, height=6, wrap="word", font=("Segoe UI", 11), undo=True,
                             exportselection=False)
        self.texto.grid(row=1, column=0, sticky="ew", pady=(2, 4))
        self.texto.bind("<KeyRelease>", lambda e: self.programar_actualizacion())
        self.texto.bind("<<Selection>>", lambda e: self._actualizar_seleccion())
        self.texto.bind("<ButtonRelease-1>", lambda e: self._actualizar_seleccion())
        for cid, color in COLORES.items():
            self.texto.tag_configure(cid, background=color)
        self.texto.tag_raise("sel")

        sel = ttk.Frame(izq)
        sel.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.lbl_sel = ttk.Label(sel, text="Selecciona texto con el mouse y elige un cifrado", foreground="#444")
        self.lbl_sel.pack(side="left")
        self.var_sel = tk.StringVar(value=PLACEHOLDER_SEL)
        self.combo_sel = ttk.Combobox(sel, textvariable=self.var_sel, values=NOMBRES[:-1],
                                      state="readonly", width=22, exportselection=False)
        self.combo_sel.pack(side="right")
        self.combo_sel.bind("<<ComboboxSelected>>", lambda e: self.crear_tramo_desde_seleccion())

        cab = ttk.Frame(izq)
        cab.grid(row=3, column=0, sticky="ew")
        ttk.Label(cab, text="Tramos de cifrado", font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(cab, text="+ Agregar tramo", command=self.agregar_tramo).pack(side="right")

        cont = ttk.Frame(izq)
        cont.grid(row=4, column=0, sticky="nsew", pady=(4, 4))
        cont.rowconfigure(0, weight=1)
        cont.columnconfigure(0, weight=1)
        self.lienzo_tramos = tk.Canvas(cont, highlightthickness=0, bd=0)
        barra = ttk.Scrollbar(cont, orient="vertical", command=self.lienzo_tramos.yview)
        self.lienzo_tramos.configure(yscrollcommand=barra.set)
        self.lienzo_tramos.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        self.marco_tramos = ttk.Frame(self.lienzo_tramos)
        self._ventana_tramos = self.lienzo_tramos.create_window((0, 0), window=self.marco_tramos, anchor="nw")
        self.marco_tramos.bind("<Configure>", lambda e: self.lienzo_tramos.configure(
            scrollregion=self.lienzo_tramos.bbox("all")))
        self.lienzo_tramos.bind("<Configure>", lambda e: self.lienzo_tramos.itemconfigure(
            self._ventana_tramos, width=e.width))

        self.info = ttk.Label(izq, text="", foreground="#444", wraplength=380, justify="left")
        self.info.grid(row=5, column=0, sticky="w", pady=(0, 8))

        opciones = ttk.LabelFrame(izq, text="Salida", padding=8)
        opciones.grid(row=6, column=0, sticky="ew")
        opciones.columnconfigure(1, weight=1)
        ttk.Label(opciones, text="Título (opcional):").grid(row=0, column=0, sticky="w")
        self.var_titulo = tk.StringVar()
        ttk.Entry(opciones, textvariable=self.var_titulo).grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.var_leyenda = tk.BooleanVar(value=True)
        ttk.Checkbutton(opciones, text="Incluir leyenda de cifrados (página aparte)",
                        variable=self.var_leyenda).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        ttk.Label(opciones, text="Impresora:").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.var_impresora = tk.StringVar()
        self.combo_impresoras = ttk.Combobox(opciones, textvariable=self.var_impresora, state="readonly")
        self.combo_impresoras.grid(row=2, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))
        self._cargar_impresoras()

        copiar = ttk.Frame(opciones)
        copiar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(copiar, text="Copiar texto", command=self.copiar_texto).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(copiar, text="Copiar imagen", command=self.copiar_imagen).pack(side="left", expand=True, fill="x", padx=(4, 0))
        self.lbl_copiado = ttk.Label(opciones, text="", foreground="#06703a")
        self.lbl_copiado.grid(row=4, column=0, columnspan=2, sticky="w")

        botones = ttk.Frame(opciones)
        botones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(botones, text="Guardar PDF…", command=self.guardar_pdf).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_imprimir = ttk.Button(botones, text="Imprimir", command=self.imprimir)
        self.btn_imprimir.pack(side="left", expand=True, fill="x", padx=(4, 0))
        if impresion is None:
            self.btn_imprimir.state(["disabled"])

        der = ttk.Frame(raiz)
        der.grid(row=0, column=1, sticky="nsew")
        der.rowconfigure(1, weight=1)
        der.columnconfigure(0, weight=1)
        ttk.Label(der, text="Vista previa", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.vista = tk.Canvas(der, bg="white", highlightthickness=1, highlightbackground="#bbb")
        barra_v = ttk.Scrollbar(der, orient="vertical", command=self.vista.yview)
        self.vista.configure(yscrollcommand=barra_v.set)
        self.vista.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        barra_v.grid(row=1, column=1, sticky="ns", pady=(2, 0))
        self.vista.bind("<MouseWheel>", lambda e: self.vista.yview_scroll(-int(e.delta / 120), "units"))

    def _cargar_impresoras(self):
        if impresion is None:
            self.combo_impresoras.configure(values=["(pywin32 no disponible)"])
            return
        try:
            nombres, predeterminada = impresion.listar_impresoras()
        except Exception:
            nombres, predeterminada = [], ""
        self.combo_impresoras.configure(values=nombres)
        if predeterminada in nombres:
            self.var_impresora.set(predeterminada)
        elif nombres:
            self.var_impresora.set(nombres[0])

    # ---------- tramos ----------
    def agregar_tramo(self, cifrado=ORDEN[0], longitud=5):
        fila = FilaTramo(self.marco_tramos, len(self.filas) + 1,
                         self.programar_actualizacion, self.quitar_tramo, cifrado, longitud)
        fila.pack(fill="x", pady=2)
        self.filas.append(fila)
        self.programar_actualizacion()

    # ---------- selección con el mouse ----------
    def _seleccion(self):
        """(letras antes de la selección, letras dentro de la selección); se recuerda la
        última selección válida por si otro widget la borra."""
        try:
            inicio = contar_letras(self.texto.get("1.0", "sel.first"))
            dentro = contar_letras(self.texto.get("sel.first", "sel.last"))
            if dentro:
                self._sel_rango = (inicio, dentro)
        except tk.TclError:
            pass
        return self._sel_rango

    def _actualizar_seleccion(self):
        rango = self._seleccion()
        if rango:
            self.lbl_sel.config(text=f"Selección: {rango[1]} letras →", foreground="#000")
        else:
            self.lbl_sel.config(text="Selecciona texto con el mouse y elige un cifrado", foreground="#444")

    def crear_tramo_desde_seleccion(self):
        nombre_cifrado = self.var_sel.get()
        self.var_sel.set(PLACEHOLDER_SEL)
        if nombre_cifrado not in ID_POR_NOMBRE:
            return
        rango = self._seleccion()
        if not rango:
            messagebox.showinfo("Sin selección", "Primero selecciona con el mouse el texto que quieres cifrar.")
            return
        inicio, cuantas = rango
        asig = asignacion(self.tramos(), contar_letras(self.mensaje()))
        for i in range(inicio, min(inicio + cuantas, len(asig))):
            asig[i] = ID_POR_NOMBRE[nombre_cifrado]
        self._reconstruir_filas(tramos_desde_asignacion(asig))
        self.texto.tag_remove("sel", "1.0", "end")
        self._sel_rango = None
        self._actualizar_seleccion()
        self.texto.focus_set()

    def _reconstruir_filas(self, tramos):
        for f in self.filas:
            f.destroy()
        self.filas = []
        for t in tramos:
            self.agregar_tramo(t.cifrado, t.longitud)
        self.programar_actualizacion()

    def _colorear_texto(self, tramos):
        for cid in COLORES:
            self.texto.tag_remove(cid, "1.0", "end")
        cola = [t.cifrado for t in tramos for _ in range(max(0, t.longitud))]
        for i, ch in enumerate(self.texto.get("1.0", "end-1c")):
            if not contar_letras(ch):
                continue
            cid = cola.pop(0) if cola else None
            if cid:
                self.texto.tag_add(cid, f"1.0+{i}c", f"1.0+{i + 1}c")

    def quitar_tramo(self, fila):
        self.filas.remove(fila)
        fila.destroy()
        for i, f in enumerate(self.filas, 1):
            f.renumerar(i)
        self.programar_actualizacion()

    def tramos(self):
        return [f.tramo() for f in self.filas]

    def mensaje(self):
        return self.texto.get("1.0", "end-1c")

    # ---------- vista previa ----------
    def programar_actualizacion(self):
        if self._pendiente:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(80, self.actualizar)

    def actualizar(self):
        self._pendiente = None
        texto, tramos = self.mensaje(), self.tramos()
        letras = contar_letras(texto)
        asig = asignacion(tramos, letras)
        cifradas = sum(1 for c in asig if c and c != SIN_CIFRAR)
        sin_cifrar = letras - cifradas
        sobran = max(0, sum(t.longitud for t in tramos) - letras)
        partes = [f"Letras: {letras}", f"cifradas: {cifradas}"]
        if sin_cifrar:
            partes.append(f"sin cifrar: {sin_cifrar}")
        if sobran:
            partes.append(f"sobran {sobran} en los tramos")
        self.info.config(text="  ·  ".join(partes), foreground="#b00" if sin_cifrar else "#444")
        self._colorear_texto(tramos)

        self.vista.delete("all")
        margen = 20
        ancho = max(200, self.vista.winfo_width() - 2 * margen)
        dib = TkDibujante(self.vista)
        est = Estilo(tam_texto=18, tam_glifo=26)
        y = margen
        for ln in distribuir(dib, construir_tokens(texto, tramos), ancho, est):
            dibujar_linea(dib, ln, margen, y, est)
            y += est.alto_linea + est.interlineado
        self.vista.configure(scrollregion=(0, 0, ancho + 2 * margen, y + margen))

    # ---------- salida ----------
    def _validar(self):
        if contar_letras(self.mensaje()) == 0:
            messagebox.showwarning("Mensaje vacío", "Escribe un mensaje con al menos una letra.")
            return False
        if sum(t.longitud for t in self.tramos()) == 0:
            messagebox.showwarning("Sin tramos", "Define al menos un tramo con longitud mayor a 0.")
            return False
        return True

    def _avisar(self, msg):
        self.lbl_copiado.config(text=msg)
        self.after(3000, lambda: self.lbl_copiado.config(text=""))

    def copiar_texto(self):
        if not self._validar():
            return
        texto = a_texto_plano(construir_tokens(self.mensaje(), self.tramos()))
        try:
            portapapeles.copiar_texto(texto)
        except Exception as e:
            messagebox.showerror("Error al copiar", str(e))
            return
        self._avisar("Texto copiado: pégalo en WhatsApp")

    def copiar_imagen(self):
        if not self._validar():
            return
        try:
            portapapeles.copiar_imagen(renderizar_mensaje(construir_tokens(self.mensaje(), self.tramos())))
        except Exception as e:
            messagebox.showerror("Error al copiar", str(e))
            return
        self._avisar("Imagen copiada: pégala en WhatsApp")

    def guardar_pdf(self):
        if not self._validar():
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar PDF", defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")], initialfile="mensaje_cifrado.pdf")
        if not ruta:
            return
        try:
            generar_pdf(ruta, self.mensaje(), self.tramos(), self.var_leyenda.get(), self.var_titulo.get().strip())
        except Exception as e:
            messagebox.showerror("Error al generar PDF", str(e))
            return
        if messagebox.askyesno("PDF generado", f"Se guardó:\n{ruta}\n\n¿Abrirlo ahora?"):
            os.startfile(ruta)

    def imprimir(self):
        if impresion is None or not self._validar():
            return
        impresora = self.var_impresora.get()
        if not impresora:
            messagebox.showwarning("Sin impresora", "No se encontró ninguna impresora.")
            return
        if not messagebox.askyesno("Imprimir", f"¿Enviar el mensaje a:\n{impresora}?"):
            return
        try:
            impresion.imprimir(self.mensaje(), self.tramos(), self.var_leyenda.get(),
                               self.var_titulo.get().strip(), impresora)
        except Exception as e:
            messagebox.showerror("Error al imprimir", str(e))
            return
        messagebox.showinfo("Impresión", "El documento se envió a la impresora.")
