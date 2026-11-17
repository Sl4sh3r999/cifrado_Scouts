"""Backend de dibujo sobre un DC de impresora de Windows (GDI).
Recibe coordenadas en puntos (1/72") y las convierte a píxeles del dispositivo."""
import win32ui
import win32con
from .dibujo import Dibujante


class GdiDibujante(Dibujante):
    def __init__(self, dc, dpi_x, dpi_y, fuente="Arial"):
        self.dc = dc
        self.sx, self.sy = dpi_x / 72, dpi_y / 72
        self.fuente = fuente
        self._fuentes, self._plumas = {}, {}
        self.dc.SetBkMode(win32con.TRANSPARENT)
        self.dc.SetTextColor(0)
        self._brocha = win32ui.CreateBrush(win32con.BS_SOLID, 0, 0)
        self.dc.SelectObject(self._brocha)

    def _px(self, x, y):
        return int(round(x * self.sx)), int(round(y * self.sy))

    def _fuente_gdi(self, tam, negrita):
        clave = (round(tam * 10), negrita)
        if clave not in self._fuentes:
            self._fuentes[clave] = win32ui.CreateFont({
                "name": self.fuente,
                "height": -int(round(tam * self.sy)),
                "weight": 700 if negrita else 400,
                "charset": win32con.DEFAULT_CHARSET,
            })
        return self._fuentes[clave]

    def _pluma(self, grosor_px):
        if grosor_px not in self._plumas:
            self._plumas[grosor_px] = win32ui.CreatePen(win32con.PS_SOLID, grosor_px, 0)
        return self._plumas[grosor_px]

    def linea(self, x1, y1, x2, y2, grosor=1.5):
        anterior = self.dc.SelectObject(self._pluma(max(1, int(round(grosor * self.sx)))))
        self.dc.MoveTo(self._px(x1, y1))
        self.dc.LineTo(self._px(x2, y2))
        self.dc.SelectObject(anterior)

    def punto(self, x, y, radio):
        cx, cy = self._px(x, y)
        r = max(1, int(round(radio * self.sx)))
        anterior = self.dc.SelectObject(self._pluma(1))
        self.dc.Ellipse((cx - r, cy - r, cx + r, cy + r))
        self.dc.SelectObject(anterior)

    def texto(self, x, y, txt, tam, negrita=False):
        anterior = self.dc.SelectObject(self._fuente_gdi(tam, negrita))
        px, py = self._px(x, y)
        self.dc.TextOut(px, py, txt)
        self.dc.SelectObject(anterior)

    def ancho_texto(self, txt, tam, negrita=False):
        anterior = self.dc.SelectObject(self._fuente_gdi(tam, negrita))
        w, _ = self.dc.GetTextExtent(txt)
        self.dc.SelectObject(anterior)
        return w / self.sx

    def alto_texto(self, tam):
        anterior = self.dc.SelectObject(self._fuente_gdi(tam, False))
        _, h = self.dc.GetTextExtent("Ag")
        self.dc.SelectObject(anterior)
        return h / self.sy
