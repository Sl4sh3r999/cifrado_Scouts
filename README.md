# Codificador de mensajes

Programa portable para Windows que cifra un mensaje combinando varios cifrados
por tramos y genera un documento imprimible (PDF o impresión directa).

## Cifrados incluidos

| Cifrado | Regla |
|---|---|
| **Numérico** | A=1, B=2 … Ñ=15 … Z=27. Los números de una palabra van unidos por guiones. |
| **Gato (Clave Vieja)** | Pigpen sobre una cuadrícula 3×3 de celdas con 3 letras cada una. Se dibuja el contorno de la celda y un punto debajo (izq./centro/der.) según sea la 1ª, 2ª o 3ª letra. |
| **Inversa (espejo)** | Atbash: A↔Z, B↔Y, C↔X … (Ñ↔M). |
| **Siete cruces** | 7 cruces en X (1-7) con 4 gajos cada una: arriba, derecha, abajo, izquierda (1=A B C D, 2=E F G H, 3=I J K L, 4=M N Ñ O, 5=P Q R S, 6=T U V W, 7=X Y Z). Cada letra es un chevron del gajo (∨ ∧ > <) con el número de su cruz dentro. |
| **Cenit Polar** | C E N I T ↔ P O L A R (cada letra se cambia por la de la otra fila). CREATIVIDAD → PTOIRAVADID. |
| **Radiofónico** | Cada letra se reemplaza por su palabra: A=Alpha, B=Bravo … Z=Zulu (Ñ=Eñe). Las palabras del mensaje se separan con "/". |
| **Murciélago** | M U R C I E L A G O → 0 1 2 3 4 5 6 7 8 9. Las demás letras no cambian. |

El alfabeto es el español de 27 letras (con Ñ). Acentos se eliminan, espacios y
puntuación pasan sin cifrar.

## Uso

1. Escribe el mensaje.
2. Define los **tramos**: selecciona con el mouse una parte del mensaje y elige
   un cifrado en *Cifrar selección como…*; se crea un tramo con ese número de
   letras. También puedes agregar tramos a mano y ajustar su longitud. El texto
   del mensaje se colorea según el cifrado que cubre cada parte. Las letras que
   no cubre ningún tramo se imprimen sin cifrar (el contador lo avisa en rojo).
3. Revisa la vista previa.
4. **Copiar texto** deja el mensaje cifrado en el portapapeles para pegarlo en
   WhatsApp u otro chat (Gato se escribe con la forma de la celda y 1-3 puntos,
   p. ej. `┘••`; Siete cruces como `∨2 ∧5`). **Copiar imagen** copia el dibujo
   exacto del mensaje, ideal para los cifrados gráficos.
5. **Guardar PDF…** genera el archivo, o **Imprimir** lo manda directo a la
   impresora elegida. Con *Incluir leyenda* se añade una página con la clave de
   cada cifrado usado.

## Ejecutar desde código

```bash
py -m pip install --user reportlab pywin32 pillow
py src\main.py
```

## Compilar el ejecutable portable

```bash
py -m pip install --user pyinstaller
powershell -ExecutionPolicy Bypass -File build\build.ps1
```

El resultado es `dist\Codificador.exe`: un solo archivo, sin instalación.

## Estructura

```
src/
  main.py               punto de entrada
  ciphers/              un módulo por cifrado + registro/tramos
  render/dibujo.py      compositor (distribución en líneas, dibujo de glifos)
  render/tk_drawer.py   backend vista previa (tkinter)
  render/pdf_drawer.py  backend PDF (reportlab)
  render/gdi_drawer.py  backend impresora (GDI / pywin32)
  render/documento.py   flujo paginado: mensaje + leyenda
  pdf/exportar.py       generar PDF
  impresion.py          impresión directa
  ui/app.py             interfaz gráfica
```
