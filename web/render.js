"use strict";
// Port de src/render/*.py: compositor de líneas, glifos y documento paginado.
// Los "dibujantes" (canvas / jsPDF) implementan: linea, punto, texto, anchoTexto, altoTexto.

class Estilo {
  constructor(o = {}) {
    this.tamTexto = 16; this.tamGlifo = 24; this.sep = 5; this.sepGlifo = 11;
    this.espacioPalabra = 18; this.interlineado = 14;
    Object.assign(this, o);
  }
  get altoGlifo() { return this.tamGlifo * 1.05; }
  get altoLinea() { return Math.max(this.altoGlifo, this.tamTexto * 1.3); }
}

function separador(prev, tok, est) {
  if (!prev) return [0, null];
  if (prev.tipo === "texto" && tok.tipo === "texto") {
    if (prev.cifrado === "numerico" && tok.cifrado === "numerico") return [est.sep, "-"];
    if (prev.cifrado === tok.cifrado) return [tok.cifrado === "radiofonico" ? est.sep * 2 : 0, null];
    return [est.sep * 2, null];
  }
  if (prev.tipo === "glifo" && tok.tipo === "glifo") return [est.sepGlifo, null];
  return [est.sep * 2, null];
}

function agruparPalabras(tokens) {
  const res = [];
  let actual = [];
  for (const tok of tokens) {
    if (tok.tipo === "espacio" || tok.tipo === "salto") {
      if (actual.length) { res.push(actual); actual = []; }
      res.push([tok]);
    } else actual.push(tok);
  }
  if (actual.length) res.push(actual);
  return res;
}

function distribuir(dib, tokens, anchoMax, est) {
  const lineas = [{ items: [], ancho: 0 }];
  const nuevaLinea = () => lineas.push({ items: [], ancho: 0 });
  const palabras = agruparPalabras(tokens);

  palabras.forEach((palabra, i) => {
    if (palabra[0].tipo === "salto") { nuevaLinea(); return; }
    if (palabra[0].tipo === "espacio") {
      const linea = lineas[lineas.length - 1];
      if (!linea.items.length) return;
      const junto = (i > 0 && usaBarra(palabras[i - 1][palabras[i - 1].length - 1])) ||
                    (i + 1 < palabras.length && usaBarra(palabras[i + 1][0]));
      if (junto) {
        const w = dib.anchoTexto("/", est.tamTexto);
        linea.ancho += est.sep * 2;
        linea.items.push({ token: { tipo: "texto", valor: "/", cifrado: null }, x: linea.ancho, ancho: w });
        linea.ancho += w + est.sep * 2;
      } else linea.ancho += est.espacioPalabra;
      return;
    }

    const piezas = [];
    let prev = null;
    for (const tok of palabra) {
      const items = [];
      let x = 0;
      const [hueco, sepTxt] = separador(prev, tok, est);
      if (sepTxt) {
        const w = dib.anchoTexto(sepTxt, est.tamTexto);
        items.push({ token: { tipo: "texto", valor: sepTxt, cifrado: null }, x: x + hueco / 2, ancho: w });
        x += hueco / 2 + w + hueco / 2;
      } else x += hueco;
      const w = tok.tipo === "glifo" ? est.tamGlifo : dib.anchoTexto(tok.valor, est.tamTexto);
      items.push({ token: tok, x, ancho: w });
      piezas.push({ items, ancho: x + w, hueco });
      prev = tok;
    }

    const total = piezas.reduce((s, p) => s + p.ancho, 0);
    let linea = lineas[lineas.length - 1];
    if (linea.items.length && linea.ancho + total > anchoMax) { nuevaLinea(); linea = lineas[lineas.length - 1]; }
    const partir = total > anchoMax;
    piezas.forEach((p, k) => {
      let anchoP = p.ancho;
      if (partir && k && linea.items.length && linea.ancho + anchoP > anchoMax) {
        nuevaLinea(); linea = lineas[lineas.length - 1];
        for (const it of p.items) it.x -= p.hueco;
        anchoP -= p.hueco;
      }
      const base = linea.ancho;
      for (const it of p.items) it.x += base;
      linea.items.push(...p.items);
      linea.ancho = base + anchoP;
    });
  });
  if (lineas.length && !lineas[lineas.length - 1].items.length) lineas.pop();
  return lineas;
}

function dibujarGajo(dib, g, x, y, s, grosor) {
  const a = 0.06, b = 0.94, v = 0.5;
  let pts, centro;
  if (g.lado === "arriba") { pts = [[a, a], [v, b], [b, a]]; centro = [0.5, 0.33]; }
  else if (g.lado === "abajo") { pts = [[a, b], [v, a], [b, b]]; centro = [0.5, 0.67]; }
  else if (g.lado === "izq") { pts = [[a, a], [b, v], [a, b]]; centro = [0.33, 0.5]; }
  else { pts = [[b, a], [a, v], [b, b]]; centro = [0.67, 0.5]; }
  for (let i = 0; i < 2; i++) {
    dib.linea(x + pts[i][0] * s, y + pts[i][1] * s, x + pts[i + 1][0] * s, y + pts[i + 1][1] * s, grosor);
  }
  const tam = s * 0.4, txt = String(g.numero);
  const w = dib.anchoTexto(txt, tam), h = dib.altoTexto(tam);
  dib.texto(x + centro[0] * s - w / 2, y + centro[1] * s - h / 2, txt, tam);
}

function dibujarGlifo(dib, g, x, y, s, grosor = 1.6) {
  if (g.tipo === "siete") { dibujarGajo(dib, g, x, y, s, grosor); return; }
  if (g.sup) dib.linea(x, y, x + s, y, grosor);
  if (g.inf) dib.linea(x, y + s, x + s, y + s, grosor);
  if (g.izq) dib.linea(x, y, x, y + s, grosor);
  if (g.der) dib.linea(x + s, y, x + s, y + s, grosor);
  dib.punto(x + s * [0.22, 0.5, 0.78][g.punto], y + s * 0.74, s * 0.08);
}

function dibujarLinea(dib, linea, x0, y, est) {
  const yTxt = y + (est.tamGlifo - dib.altoTexto(est.tamTexto)) / 2;
  for (const it of linea.items) {
    if (it.token.tipo === "glifo") dibujarGlifo(dib, it.token.valor, x0 + it.x, y, est.tamGlifo);
    else dib.texto(x0 + it.x, yTxt, it.token.valor, est.tamTexto);
  }
}

// ---------- documento paginado (PDF) ----------
class Documento {
  constructor(dib, ancho, alto, margen, nuevaPagina) {
    this.dib = dib; this.w = ancho; this.h = alto; this.m = margen;
    this.nueva = nuevaPagina; this.y = margen;
  }
  get anchoUtil() { return this.w - 2 * this.m; }
  saltoPagina() { this.nueva(); this.y = this.m; }
  asegurar(alto) { if (this.y + alto > this.h - this.m) this.saltoPagina(); }
  titulo(txt, tam = 16) {
    this.asegurar(tam * 2);
    this.dib.texto(this.m, this.y, txt, tam, true);
    this.y += tam * 1.8;
  }
  parrafo(txt, tam = 10) {
    const lineas = [];
    let actual = "";
    for (const palabra of txt.split(/\s+/)) {
      const prueba = `${actual} ${palabra}`.trim();
      if (actual && this.dib.anchoTexto(prueba, tam) > this.anchoUtil) { lineas.push(actual); actual = palabra; }
      else actual = prueba;
    }
    if (actual) lineas.push(actual);
    for (const l of lineas) {
      this.asegurar(tam * 1.4);
      this.dib.texto(this.m, this.y, l, tam);
      this.y += tam * 1.4;
    }
    this.y += tam * 0.6;
  }
  mensaje(tokens, est) {
    for (const ln of distribuir(this.dib, tokens, this.anchoUtil, est)) {
      this.asegurar(est.altoLinea);
      dibujarLinea(this.dib, ln, this.m, this.y, est);
      this.y += est.altoLinea + est.interlineado;
    }
  }
  leyenda(usados) {
    this.titulo("Leyenda de cifrados", 18);
    for (const cid of usados) {
      this.asegurar(CIFRADOS[cid].grafico ? 200 : 140);
      this.titulo(nombreCifrado(cid), 13);
      this.parrafo(CIFRADOS[cid].desc);
      if (cid === "murcielago") this.leyendaMurcielago();
      else if (CIFRADOS[cid].grafico) this.leyendaGlifos(cid, cid === "gato" ? 9 : 8, cid === "gato" ? 3 : 4);
      else this.leyendaTabla(leyendaFilas(cid), cid === "radiofonico" ? 4 : 9);
      this.y += 12;
    }
  }
  leyendaTabla(filas, porFila, tam = 11) {
    const ancho = this.anchoUtil / porFila;
    for (let i = 0; i < filas.length; i += porFila) {
      this.asegurar(tam * 1.6);
      filas.slice(i, i + porFila).forEach(([l, v], j) => this.dib.texto(this.m + j * ancho, this.y, `${l} = ${v}`, tam));
      this.y += tam * 1.6;
    }
  }
  leyendaMurcielago(tam = 13) {
    this.asegurar(tam * 3.2);
    [...MURCIELAGO].forEach((l, i) => {
      const x = this.m + i * 28;
      this.dib.texto(x, this.y, l, tam, true);
      this.dib.texto(x, this.y + tam * 1.4, String(i), tam);
    });
    this.y += tam * 3.2;
  }
  leyendaGlifos(cid, porFila, grupo, tamGlifo = 20, tamLetra = 11) {
    const filas = leyendaFilas(cid);
    const huecoGrupo = 10;
    const anchoCelda = (this.anchoUtil - Math.floor(porFila / grupo) * huecoGrupo) / porFila;
    const altoFila = tamLetra * 1.4 + tamGlifo * 1.1 + 10;
    for (let i = 0; i < filas.length; i += porFila) {
      this.asegurar(altoFila);
      filas.slice(i, i + porFila).forEach(([l, g], j) => {
        const x = this.m + j * anchoCelda + Math.floor(j / grupo) * huecoGrupo + (anchoCelda - tamGlifo) / 2;
        const lw = this.dib.anchoTexto(l, tamLetra, true);
        this.dib.texto(x + (tamGlifo - lw) / 2, this.y, l, tamLetra, true);
        dibujarGlifo(this.dib, g, x, this.y + tamLetra * 1.4, tamGlifo);
      });
      this.y += altoFila;
    }
  }
}

// ---------- dibujantes ----------
class CanvasDibujante {
  constructor(ctx) { this.c = ctx; }
  linea(x1, y1, x2, y2, grosor = 1.5) {
    const c = this.c;
    c.strokeStyle = "#111"; c.lineWidth = grosor; c.lineCap = "round";
    c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke();
  }
  punto(x, y, r) { const c = this.c; c.fillStyle = "#111"; c.beginPath(); c.arc(x, y, r, 0, 2 * Math.PI); c.fill(); }
  texto(x, y, txt, tam, negrita = false) {
    const c = this.c;
    c.font = `${negrita ? "bold " : ""}${tam}px Arial, Helvetica, sans-serif`;
    c.fillStyle = "#111"; c.textBaseline = "top"; c.fillText(txt, x, y);
  }
  anchoTexto(txt, tam, negrita = false) {
    this.c.font = `${negrita ? "bold " : ""}${tam}px Arial, Helvetica, sans-serif`;
    return this.c.measureText(txt).width;
  }
  altoTexto(tam) { return tam * 1.2; }
}

class PdfDibujante {
  constructor(doc) { this.d = doc; }
  linea(x1, y1, x2, y2, grosor = 1.5) {
    this.d.setDrawColor(0); this.d.setLineWidth(grosor); this.d.setLineCap("round");
    this.d.line(x1, y1, x2, y2);
  }
  punto(x, y, r) { this.d.setFillColor(0); this.d.circle(x, y, r, "F"); }
  texto(x, y, txt, tam, negrita = false) {
    this.d.setFont("helvetica", negrita ? "bold" : "normal");
    this.d.setFontSize(tam); this.d.setTextColor(0);
    this.d.text(txt, x, y + tam * 0.9);
  }
  anchoTexto(txt, tam, negrita = false) {
    this.d.setFont("helvetica", negrita ? "bold" : "normal");
    this.d.setFontSize(tam);
    return this.d.getTextWidth(txt);
  }
  altoTexto(tam) { return tam * 1.2; }
}

function usadosEn(tokens) {
  return ORDEN.filter((cid) => tokens.some((t) => t.cifrado === cid));
}

// Dibuja el mensaje en un canvas (vista previa o imagen). Devuelve el canvas.
function renderizarMensaje(canvas, tokens, ancho, escala, est = new Estilo({ tamTexto: 18, tamGlifo: 26 }), margen = 16) {
  const medidor = new CanvasDibujante(document.createElement("canvas").getContext("2d"));
  const lineas = distribuir(medidor, tokens, ancho - 2 * margen, est);
  const alto = Math.ceil(2 * margen + Math.max(1, lineas.length) * (est.altoLinea + est.interlineado));
  canvas.width = Math.round(ancho * escala);
  canvas.height = Math.round(alto * escala);
  canvas.style.width = ancho + "px";
  canvas.style.height = alto + "px";
  const ctx = canvas.getContext("2d");
  ctx.setTransform(escala, 0, 0, escala, 0, 0);
  ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, ancho, alto);
  const dib = new CanvasDibujante(ctx);
  let y = margen;
  for (const ln of lineas) { dibujarLinea(dib, ln, margen, y, est); y += est.altoLinea + est.interlineado; }
  return canvas;
}

function generarPdf(texto, tramos, incluirLeyenda, titulo) {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ unit: "pt", format: "letter" });
  const dib = new PdfDibujante(doc);
  const d = new Documento(dib, 612, 792, 56, () => doc.addPage());
  if (titulo) { d.titulo(titulo, 18); d.y += 6; }
  const tokens = construirTokens(texto, tramos);
  d.mensaje(tokens, new Estilo());
  const usados = usadosEn(tokens);
  if (incluirLeyenda && usados.length) { d.saltoPagina(); d.leyenda(usados); }
  doc.setProperties({ title: titulo || "Mensaje cifrado" });
  return doc;
}
