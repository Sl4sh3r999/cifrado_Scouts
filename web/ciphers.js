"use strict";
// Port de src/ciphers/*.py. Mantener sincronizado con la versión de escritorio.

const ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ";
const INDICE = new Map([...ALFABETO].map((l, i) => [l, i]));
const PUNTUACION = " .,;:!?¡¿-'/()\n0123456789";
const SIN_CIFRAR = "ninguno";

function normalizar(texto) {
  let salida = "";
  for (const ch of texto.toUpperCase()) {
    salida += ch === "Ñ" ? ch : ch.normalize("NFD").replace(/\p{M}/gu, "");
  }
  return [...salida].filter((c) => INDICE.has(c) || PUNTUACION.includes(c)).join("");
}

function letraDe(ch) {
  const n = normalizar(ch);
  return n.length === 1 && INDICE.has(n) ? n : null;
}

function contarLetras(texto) {
  let n = 0;
  for (const ch of texto) if (letraDe(ch)) n++;
  return n;
}

// ---------- cifrados de texto ----------
const MURCIELAGO = "MURCIELAGO";
const CENIT = "CENIT", POLAR = "POLAR";
const PALABRAS_RADIO = {
  A: "Alpha", B: "Bravo", C: "Charlie", D: "Delta", E: "Echo", F: "Foxtrot", G: "Golf",
  H: "Hotel", I: "India", J: "Juliett", K: "Kilo", L: "Lima", M: "Mike", N: "November",
  Ñ: "Eñe", O: "Oscar", P: "Papa", Q: "Quebec", R: "Romeo", S: "Sierra", T: "Tango",
  U: "Uniform", V: "Victor", W: "Whiskey", X: "X-ray", Y: "Yankee", Z: "Zulu",
};
const MAPA_CENIT = {};
[...CENIT].forEach((a, i) => { MAPA_CENIT[a] = POLAR[i]; MAPA_CENIT[POLAR[i]] = a; });

// ---------- cifrados gráficos ----------
function glifoGato(i) {
  const celda = Math.floor(i / 3);
  const fila = Math.floor(celda / 3), col = celda % 3;
  return { tipo: "gato", izq: col > 0, der: col < 2, sup: fila > 0, inf: fila < 2, punto: i % 3 };
}

const LADOS = ["arriba", "der", "abajo", "izq"];
const CRUCES = ["ABCD", "EFGH", "IJKL", "MNÑO", "PQRS", "TUVW", "XYZ"];
const GLIFOS_7 = {};
CRUCES.forEach((letras, n) => [...letras].forEach((l, k) => {
  GLIFOS_7[l] = { tipo: "siete", lado: LADOS[k], numero: n + 1 };
}));

const FORMAS_GATO = {
  "0101": "┘", "1001": "└", "1101": "⊔", "0111": "⊐", "1111": "□",
  "1011": "⊏", "0110": "┐", "1010": "┌", "1110": "⊓",
};
const SIMBOLOS_7 = { arriba: "∨", abajo: "∧", izq: ">", der: "<" };

function gatoATexto(g) {
  const k = [g.izq, g.der, g.sup, g.inf].map((b) => (b ? "1" : "0")).join("");
  return FORMAS_GATO[k] + "•".repeat(g.punto + 1);
}

const CIFRADOS = {
  numerico: {
    id: "numerico", nombre: "Numérico", color: "#cfe3ff",
    desc: "Cada letra se sustituye por su posición en el alfabeto (A=1 ... Z=27). Los números de una misma palabra van separados por guiones.",
    cifrar: (ch) => String(INDICE.get(ch) + 1),
  },
  gato: {
    id: "gato", nombre: "Gato (Clave Vieja)", color: "#ffd9a8", grafico: true,
    desc: "Se dibuja el contorno de la celda donde está la letra, más un punto dentro (izquierda, centro o derecha) según sea la 1a, 2a o 3a letra de esa celda.",
    cifrar: (ch) => glifoGato(INDICE.get(ch)),
    aTexto: gatoATexto,
  },
  inversa: {
    id: "inversa", nombre: "Inversa (espejo)", color: "#cdf2c9",
    desc: "Cada letra se sustituye por su opuesta en el alfabeto (A<->Z, B<->Y, C<->X...).",
    cifrar: (ch) => ALFABETO[ALFABETO.length - 1 - INDICE.get(ch)],
  },
  murcielago: {
    id: "murcielago", nombre: "Murciélago", color: "#efcdf5",
    desc: "Las letras de la palabra MURCIELAGO se sustituyen por su posición (0-9). Las demás letras se escriben tal cual.",
    cifrar: (ch) => { const i = MURCIELAGO.indexOf(ch); return i >= 0 ? String(i) : ch; },
  },
  sietecruces: {
    id: "sietecruces", nombre: "Siete cruces", color: "#fff0a0", grafico: true,
    desc: "Hay 7 cruces en X numeradas del 1 al 7; cada una tiene 4 gajos (arriba, derecha, abajo, izquierda). La letra se escribe con el gajo donde está (un chevron: arriba, abajo, izquierda o derecha) y el número de su cruz dentro.",
    cifrar: (ch) => GLIFOS_7[ch],
    aTexto: (g) => SIMBOLOS_7[g.lado] + g.numero,
  },
  cenitpolar: {
    id: "cenitpolar", nombre: "Cenit Polar", color: "#b8ece8",
    desc: "Cada letra de CENIT se reemplaza por la de POLAR que está debajo, y viceversa (C<->P, E<->O, N<->L, I<->A, T<->R). Las demás letras no cambian.",
    cifrar: (ch) => MAPA_CENIT[ch] ?? ch,
  },
  radiofonico: {
    id: "radiofonico", nombre: "Radiofónico", color: "#ffc9c9", barra: true,
    desc: "Cada letra se sustituye por su palabra del alfabeto radiofónico (A = Alpha, B = Bravo ...). Las palabras de un mismo mensaje se separan con \"/\". La Ñ se dice \"Eñe\".",
    cifrar: (ch) => PALABRAS_RADIO[ch],
  },
};
const ORDEN = ["numerico", "gato", "inversa", "murcielago", "sietecruces", "cenitpolar", "radiofonico"];
const COLOR_SIN_CIFRAR = "#e6e6e6";

function nombreCifrado(id) {
  return id === SIN_CIFRAR ? "Sin cifrar" : CIFRADOS[id].nombre;
}
function colorCifrado(id) {
  return id === SIN_CIFRAR ? COLOR_SIN_CIFRAR : CIFRADOS[id].color;
}

function leyendaFilas(id) {
  return [...ALFABETO].map((l) => [l, CIFRADOS[id].cifrar(l)]);
}

// ---------- tramos y tokens ----------
function asignacion(tramos, total) {
  const cola = [];
  for (const t of tramos) for (let i = 0; i < Math.max(0, t.longitud); i++) cola.push(t.cifrado);
  while (cola.length < total) cola.push(null);
  return cola.slice(0, total);
}

function tramosDesdeAsignacion(asig) {
  let fin = asig.length;
  while (fin > 0 && asig[fin - 1] === null) fin--;
  const tramos = [];
  for (const c of asig.slice(0, fin)) {
    const cid = c || SIN_CIFRAR;
    const ult = tramos[tramos.length - 1];
    if (ult && ult.cifrado === cid) ult.longitud++;
    else tramos.push({ cifrado: cid, longitud: 1 });
  }
  return tramos;
}

function construirTokens(texto, tramos) {
  texto = normalizar(texto);
  const cola = [];
  for (const t of tramos) for (let i = 0; i < Math.max(0, t.longitud); i++) cola.push(t.cifrado);
  const tokens = [];
  for (const ch of texto) {
    if (ch === "\n") tokens.push({ tipo: "salto" });
    else if (ch === " ") tokens.push({ tipo: "espacio" });
    else if (INDICE.has(ch)) {
      const cid = cola.length ? cola.shift() : SIN_CIFRAR;
      if (cid === SIN_CIFRAR) { tokens.push({ tipo: "texto", valor: ch, cifrado: null }); continue; }
      const salida = CIFRADOS[cid].cifrar(ch);
      tokens.push({ tipo: typeof salida === "string" ? "texto" : "glifo", valor: salida, cifrado: cid });
    } else tokens.push({ tipo: "texto", valor: ch, cifrado: null });
  }
  return tokens;
}

function usaBarra(tok) {
  return tok.tipo === "glifo" || tok.cifrado === "radiofonico";
}

function aTextoPlano(tokens) {
  let salida = "";
  let prev = null, esperaSep = false;
  for (const tok of tokens) {
    if (tok.tipo === "salto") { salida += "\n"; prev = null; esperaSep = false; }
    else if (tok.tipo === "espacio") esperaSep = true;
    else {
      const valor = tok.tipo === "glifo" ? CIFRADOS[tok.cifrado].aTexto(tok.valor) : tok.valor;
      if (esperaSep && prev) salida += usaBarra(prev) || usaBarra(tok) ? " / " : " ";
      else if (prev) {
        if (prev.cifrado === "numerico" && tok.cifrado === "numerico") salida += "-";
        else if (prev.tipo === "glifo" || tok.tipo === "glifo") salida += " ";
        else if (prev.cifrado === "radiofonico" && tok.cifrado === "radiofonico") salida += " ";
        else if (prev.cifrado !== tok.cifrado) salida += " ";
      }
      salida += valor;
      prev = tok; esperaSep = false;
    }
  }
  return salida;
}
