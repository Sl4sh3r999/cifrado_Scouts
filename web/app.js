"use strict";

const $ = (id) => document.getElementById(id);
const el = { msg: $("mensaje"), res: $("resaltado"), chips: $("chips"), tramos: $("tramos"), resumen: $("resumen"),
  selInfo: $("sel-info"), vista: $("vista"), estado: $("estado"), titulo: $("titulo"), leyenda: $("leyenda") };

let tramos = [];
let seleccion = null; // {inicio, cuantas} en letras
let aviso = null;

const escapar = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

function mensaje() { return el.msg.value; }

function estado(txt, error = false) {
  el.estado.textContent = txt;
  el.estado.classList.toggle("error", error);
  clearTimeout(aviso);
  if (txt) aviso = setTimeout(() => (el.estado.textContent = ""), 4000);
}

// ---------- selección ----------
function leerSeleccion() {
  const a = el.msg.selectionStart, b = el.msg.selectionEnd;
  if (a === b) { seleccion = null; return; }
  const t = mensaje();
  const inicio = contarLetras(t.slice(0, a));
  const cuantas = contarLetras(t.slice(a, b));
  seleccion = cuantas ? { inicio, cuantas } : null;
}

function actualizarSelInfo() {
  el.selInfo.textContent = seleccion
    ? `Selección: ${seleccion.cuantas} letra${seleccion.cuantas === 1 ? "" : "s"}. Toca la clave que quieres aplicarle:`
    : "Sin selección: la clave se aplicará a todo el mensaje.";
}

function aplicarClave(cid) {
  const total = contarLetras(mensaje());
  if (!total) { estado("Escribe primero un mensaje con al menos una letra.", true); return; }
  const asig = asignacion(tramos, total);
  const { inicio, cuantas } = seleccion || { inicio: 0, cuantas: total };
  for (let i = inicio; i < Math.min(inicio + cuantas, asig.length); i++) asig[i] = cid;
  tramos = tramosDesdeAsignacion(asig);
  const fin = el.msg.selectionEnd;
  el.msg.setSelectionRange(fin, fin);
  seleccion = null;
  renderTramos();
  actualizar();
}

// ---------- UI de tramos ----------
function renderChips() {
  el.chips.innerHTML = "";
  for (const cid of ORDEN) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = CIFRADOS[cid].nombre;
    b.style.background = CIFRADOS[cid].color;
    b.addEventListener("mousedown", (e) => e.preventDefault());
    b.addEventListener("click", () => aplicarClave(cid));
    el.chips.appendChild(b);
  }
}

function renderTramos() {
  el.tramos.innerHTML = "";
  tramos.forEach((t, i) => {
    const fila = document.createElement("div");
    fila.className = "tramo";
    const sel = document.createElement("select");
    for (const cid of [...ORDEN, SIN_CIFRAR]) {
      const o = document.createElement("option");
      o.value = cid; o.textContent = nombreCifrado(cid); o.selected = cid === t.cifrado;
      sel.appendChild(o);
    }
    const color = document.createElement("span");
    color.className = "color"; color.style.background = colorCifrado(t.cifrado);
    sel.addEventListener("change", () => { t.cifrado = sel.value; color.style.background = colorCifrado(t.cifrado); actualizar(); });
    const num = document.createElement("input");
    num.type = "number"; num.min = "1"; num.max = "9999"; num.value = t.longitud;
    num.addEventListener("input", () => { t.longitud = Math.max(0, parseInt(num.value, 10) || 0); actualizar(); });
    const quitar = document.createElement("button");
    quitar.type = "button"; quitar.className = "quitar"; quitar.textContent = "Quitar";
    quitar.addEventListener("click", () => { tramos.splice(i, 1); renderTramos(); actualizar(); });
    const n = document.createElement("span");
    n.className = "n"; n.textContent = `Tramo ${i + 1}`;
    const l = document.createElement("span");
    l.textContent = "letras";
    fila.append(n, color, sel, num, l, quitar);
    el.tramos.appendChild(fila);
  });
}

// ---------- actualización ----------
function pintarResaltado() {
  const t = mensaje();
  const asig = asignacion(tramos, contarLetras(t));
  let k = 0, html = "";
  for (const ch of t) {
    if (letraDe(ch)) {
      const cid = asig[k++];
      html += cid ? `<span style="background:${colorCifrado(cid)}">${escapar(ch)}</span>` : escapar(ch);
    } else html += escapar(ch);
  }
  el.res.innerHTML = html + "\n";
  el.res.scrollTop = el.msg.scrollTop;
}

function actualizar() {
  const t = mensaje();
  const letras = contarLetras(t);
  const asig = asignacion(tramos, letras);
  const cifradas = asig.filter((c) => c && c !== SIN_CIFRAR).length;
  const sin = letras - cifradas;
  const sobran = Math.max(0, tramos.reduce((s, x) => s + x.longitud, 0) - letras);
  const partes = [`Letras: ${letras}`, `cifradas: ${cifradas}`];
  if (sin) partes.push(`sin cifrar: ${sin}`);
  if (sobran) partes.push(`sobran ${sobran} en los tramos`);
  el.resumen.textContent = partes.join(" · ");
  el.resumen.classList.toggle("alerta", sin > 0 && letras > 0);
  pintarResaltado();
  actualizarSelInfo();
  const ancho = Math.max(240, Math.min(el.vista.parentElement.clientWidth || 560, 760));
  renderizarMensaje(el.vista, construirTokens(t, tramos), ancho, window.devicePixelRatio || 1);
}

// ---------- salida ----------
function validar() {
  if (!contarLetras(mensaje())) { estado("Escribe un mensaje con al menos una letra.", true); return false; }
  if (!tramos.some((t) => t.longitud > 0 && t.cifrado !== SIN_CIFRAR)) {
    estado("Elige una clave para el mensaje (toca una de las claves de arriba).", true); return false;
  }
  return true;
}

function nombreArchivo(ext) {
  const base = (el.titulo.value || "mensaje_cifrado").trim().normalize("NFD").replace(/\p{M}/gu, "")
    .replace(/[^\w\- ]+/g, "").replace(/\s+/g, "_").slice(0, 50) || "mensaje_cifrado";
  return `${base}.${ext}`;
}

function crearPdf() {
  return generarPdf(mensaje(), tramos, el.leyenda.checked, el.titulo.value.trim());
}

function crearImagenCanvas() {
  return renderizarMensaje(document.createElement("canvas"), construirTokens(mensaje(), tramos), 560, 3);
}

const aBlob = (canvas) => new Promise((res) => canvas.toBlob(res, "image/png"));

function descargar(blob, nombre) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = nombre; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

async function compartir(archivo, titulo) {
  try { await navigator.share({ files: [archivo], title: titulo }); }
  catch (e) { if (e.name !== "AbortError") estado("No se pudo compartir: " + e.message, true); }
}

$("pdf").addEventListener("click", () => {
  if (!validar()) return;
  crearPdf().save(nombreArchivo("pdf"));
  estado("PDF descargado.");
});

$("bajar-img").addEventListener("click", async () => {
  if (!validar()) return;
  descargar(await aBlob(crearImagenCanvas()), nombreArchivo("png"));
  estado("Imagen descargada.");
});

$("copiar-texto").addEventListener("click", async () => {
  if (!validar()) return;
  try {
    await navigator.clipboard.writeText(aTextoPlano(construirTokens(mensaje(), tramos)));
    estado("Texto copiado: pégalo en WhatsApp.");
  } catch { estado("Tu navegador no permitió copiar el texto.", true); }
});

$("copiar-img").addEventListener("click", async () => {
  if (!validar()) return;
  try {
    const blob = await aBlob(crearImagenCanvas());
    await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
    estado("Imagen copiada: pégala en WhatsApp.");
  } catch { estado("Tu navegador no permite copiar imágenes; usa «Descargar imagen».", true); }
});

$("compartir-pdf").addEventListener("click", async () => {
  if (!validar()) return;
  const blob = crearPdf().output("blob");
  await compartir(new File([blob], nombreArchivo("pdf"), { type: "application/pdf" }), el.titulo.value || "Mensaje cifrado");
});

$("compartir-img").addEventListener("click", async () => {
  if (!validar()) return;
  const blob = await aBlob(crearImagenCanvas());
  await compartir(new File([blob], nombreArchivo("png"), { type: "image/png" }), el.titulo.value || "Mensaje cifrado");
});

// El menú de compartir solo se muestra si el dispositivo permite compartir archivos.
try {
  const probe = new File(["x"], "x.pdf", { type: "application/pdf" });
  if (navigator.share && navigator.canShare && navigator.canShare({ files: [probe] })) {
    $("compartir-pdf").hidden = false; $("compartir-img").hidden = false;
  }
} catch { /* sin Web Share */ }

// ---------- eventos ----------
el.msg.addEventListener("input", () => { leerSeleccion(); actualizar(); });
el.msg.addEventListener("scroll", () => (el.res.scrollTop = el.msg.scrollTop));
for (const ev of ["select", "keyup", "mouseup", "touchend"]) {
  el.msg.addEventListener(ev, () => { leerSeleccion(); actualizarSelInfo(); });
}
document.addEventListener("selectionchange", () => {
  if (document.activeElement === el.msg) { leerSeleccion(); actualizarSelInfo(); }
});
$("agregar").addEventListener("click", () => { tramos.push({ cifrado: ORDEN[0], longitud: 5 }); renderTramos(); actualizar(); });
window.addEventListener("resize", actualizar);

renderChips();
renderTramos();
actualizar();
