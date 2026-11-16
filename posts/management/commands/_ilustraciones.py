"""Ilustraciones de los posts de ejemplo, dibujadas con Pillow.

Se generan por código para que el proyecto pueda probarse desde cero sin
incluir la carpeta media/ en el repositorio.
"""
import math
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ANCHO, ALTO = 1200, 600
ESCALA = 2  # Se dibuja al doble de tamaño y se reduce al final para suavizar los bordes.

FUENTES = {
    'mono': ['consola.ttf', 'DejaVuSansMono.ttf', 'Menlo.ttc', 'LiberationMono-Regular.ttf', 'cour.ttf'],
    'negrita': ['segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf', 'Arial Bold.ttf'],
    'normal': ['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf', 'Arial.ttf'],
}

BLANCO = (255, 255, 255)


def fuente(tamanio, estilo='normal'):
    """Busca una fuente del sistema; si no encuentra ninguna usa la de Pillow."""
    for nombre in FUENTES[estilo]:
        try:
            return ImageFont.truetype(nombre, tamanio * ESCALA)
        except OSError:
            continue
    return ImageFont.load_default(size=tamanio * ESCALA)


def _e(*valores):
    return [v * ESCALA for v in valores]


class Lienzo:
    def __init__(self, color_a, color_b):
        w, h = ANCHO * ESCALA, ALTO * ESCALA
        horizontal = Image.linear_gradient('L').rotate(90).resize((w, h))
        vertical = Image.linear_gradient('L').resize((w, h))
        mascara = Image.blend(horizontal, vertical, 0.35)
        fondo = Image.composite(Image.new('RGB', (w, h), color_b), Image.new('RGB', (w, h), color_a), mascara)
        self.img = fondo.convert('RGBA')
        self.dibujo = ImageDraw.Draw(self.img)

    def _capa(self):
        return Image.new('RGBA', self.img.size, (0, 0, 0, 0))

    def manchas(self, manchas, desenfoque=70):
        capa = self._capa()
        dibujo = ImageDraw.Draw(capa)
        for x, y, r, color in manchas:
            dibujo.ellipse(_e(x - r, y - r, x + r, y + r), fill=color)
        self.img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(desenfoque * ESCALA)))

    def puntos(self, x0, y0, columnas, filas, color=(255, 255, 255, 60), separacion=22):
        capa = self._capa()
        dibujo = ImageDraw.Draw(capa)
        for i in range(columnas):
            for j in range(filas):
                cx, cy = x0 + i * separacion, y0 + j * separacion
                dibujo.ellipse(_e(cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5), fill=color)
        self.img.alpha_composite(capa)

    def sombra(self, caja, radio, opacidad=90, desplazamiento=14, desenfoque=18):
        capa = self._capa()
        x0, y0, x1, y1 = caja
        ImageDraw.Draw(capa).rounded_rectangle(
            _e(x0, y0 + desplazamiento, x1, y1 + desplazamiento), radius=radio * ESCALA, fill=(0, 0, 0, opacidad),
        )
        self.img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(desenfoque * ESCALA)))

    def rect(self, caja, color, radio=0, esquinas=None):
        if radio:
            self.dibujo.rounded_rectangle(_e(*caja), radius=radio * ESCALA, fill=color, corners=esquinas)
        else:
            self.dibujo.rectangle(_e(*caja), fill=color)

    def tarjeta(self, caja, radio, color, opacidad=90):
        self.sombra(caja, radio, opacidad=opacidad)
        self.rect(caja, color, radio)

    def circulo(self, cx, cy, r, color):
        self.dibujo.ellipse(_e(cx - r, cy - r, cx + r, cy + r), fill=color)

    def linea(self, puntos, color, ancho):
        self.dibujo.line([tuple(_e(x, y)) for x, y in puntos], fill=color, width=int(ancho * ESCALA), joint='curve')
        for x, y in (puntos[0], puntos[-1]):
            self.circulo(x, y, ancho / 2, color)

    def flecha(self, x0, y0, x1, y1, color, ancho=8, punta=24):
        angulo = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - punta * math.cos(angulo), y1 - punta * math.sin(angulo)
        self.linea([(x0, y0), (bx, by)], color, ancho)
        abertura = punta * 0.65
        izquierda = (bx + abertura * math.sin(angulo), by - abertura * math.cos(angulo))
        derecha = (bx - abertura * math.sin(angulo), by + abertura * math.cos(angulo))
        self.dibujo.polygon([tuple(_e(*p)) for p in [(x1, y1), izquierda, derecha]], fill=color)

    def texto(self, x, y, contenido, fnt, color, anchor='la'):
        self.dibujo.text(tuple(_e(x, y)), contenido, font=fnt, fill=color, anchor=anchor)

    def codigo(self, x, y, partes, fnt):
        """Escribe una línea de código formada por partes (texto, color)."""
        for contenido, color in partes:
            self.dibujo.text(tuple(_e(x, y)), contenido, font=fnt, fill=color)
            x += fnt.getlength(contenido) / ESCALA

    def nota(self, x, y, contenido, color, angulo, ancho=230, alto=150):
        """Dibuja una nota adhesiva inclinada con su sombra."""
        w, h, m = ancho * ESCALA, alto * ESCALA, 40 * ESCALA
        hoja = Image.new('RGBA', (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
        sombra = hoja.copy()
        ImageDraw.Draw(sombra).rounded_rectangle(
            (m, m + 12 * ESCALA, m + w, m + h + 12 * ESCALA), radius=8 * ESCALA, fill=(0, 0, 0, 80),
        )
        hoja.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(12 * ESCALA)))
        dibujo = ImageDraw.Draw(hoja)
        dibujo.rounded_rectangle((m, m, m + w, m + h), radius=8 * ESCALA, fill=color)
        dibujo.ellipse((m + w / 2 - 9 * ESCALA, m + 8 * ESCALA, m + w / 2 + 9 * ESCALA, m + 26 * ESCALA), fill=(220, 70, 70))
        dibujo.text((m + w / 2, m + h / 2 + 10 * ESCALA), contenido, font=fuente(26, 'negrita'), fill=(50, 50, 60), anchor='mm')
        hoja = hoja.rotate(angulo, resample=Image.BICUBIC, expand=True)
        self.img.alpha_composite(hoja, dest=(int(x * ESCALA), int(y * ESCALA)))

    def archivo(self):
        final = self.img.resize((ANCHO, ALTO), Image.LANCZOS).convert('RGB')
        buffer = BytesIO()
        final.save(buffer, format='PNG', optimize=True)
        return ContentFile(buffer.getvalue())


def _ventana(lienzo, caja, fondo, barra):
    """Ventana con barra superior y los tres botones de colores."""
    x0, y0, x1, _ = caja
    lienzo.tarjeta(caja, 18, fondo)
    lienzo.rect((x0, y0, x1, y0 + 50), barra, radio=18, esquinas=(True, True, False, False))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        lienzo.circulo(x0 + 30 + i * 24, y0 + 25, 7, color)


def ilustracion_python():
    """Editor de código con un pequeño programa en Python."""
    lienzo = Lienzo((14, 30, 58), (38, 76, 128))
    lienzo.manchas([
        (170, 130, 150, (55, 118, 171, 170)),
        (1060, 500, 190, (255, 212, 59, 120)),
        (1040, 90, 110, (75, 139, 190, 140)),
    ])
    lienzo.puntos(60, 420, 6, 6)
    lienzo.puntos(1010, 60, 6, 5)

    _ventana(lienzo, (230, 80, 970, 500), (30, 34, 44), (44, 49, 62))
    lienzo.texto(600, 105, 'primeros_pasos.py', fuente(17), (160, 168, 184), anchor='mm')

    mono = fuente(25, 'mono')
    normal, clave, cadena, funcion, comentario = (
        (224, 228, 236), (198, 120, 221), (152, 195, 121), (97, 175, 239), (110, 118, 135),
    )
    lineas = [
        [('# Mis primeros pasos en Python', comentario)],
        [('nombre = ', normal), ('"Bautista"', cadena)],
        [('cursos = [', normal), ('"Python"', cadena), (', ', normal), ('"Django"', cadena), (']', normal)],
        [],
        [('for', clave), (' curso ', normal), ('in', clave), (' cursos:', normal)],
        [('    ', normal), ('print', funcion), ('(', normal), ('f"Aprendo {curso}"', cadena), (')', normal)],
        [],
    ]
    for i, partes in enumerate(lineas):
        y = 155 + i * 44
        lienzo.texto(258, y, str(i + 1), mono, (88, 96, 112))
        lienzo.codigo(300, y, partes, mono)
    lienzo.rect((300, 155 + 6 * 44, 313, 155 + 6 * 44 + 28), funcion)

    lienzo.tarjeta((820, 455, 1010, 507), 26, (255, 212, 59))
    lienzo.texto(915, 481, 'Python 3', fuente(22, 'negrita'), (30, 40, 60), anchor='mm')
    return lienzo.archivo()


def ilustracion_poo():
    """Una función que se transforma en una clase."""
    lienzo = Lienzo((224, 112, 88), (244, 190, 130))
    lienzo.manchas([
        (150, 520, 200, (255, 255, 255, 80)),
        (1080, 80, 170, (255, 236, 200, 110)),
        (620, 300, 120, (255, 255, 255, 40)),
    ])
    lienzo.puntos(560, 70, 5, 4, color=(255, 255, 255, 90))
    lienzo.puntos(560, 450, 5, 4, color=(255, 255, 255, 90))

    oscuro, violeta, azul, verde = (52, 56, 82), (190, 80, 150), (40, 110, 200), (62, 145, 120)

    lienzo.tarjeta((90, 170, 510, 430), 20, BLANCO)
    lienzo.rect((90, 170, 510, 226), oscuro, radio=20, esquinas=(True, True, False, False))
    lienzo.texto(116, 198, 'función', fuente(24, 'negrita'), BLANCO, anchor='lm')
    mono = fuente(21, 'mono')
    lineas = [
        [('def ', violeta), ('crear_post', azul), ('(titulo):', oscuro)],
        [('    post = {', oscuro), ('"titulo"', verde), (': titulo}', oscuro)],
        [('    posts.', oscuro), ('append', azul), ('(post)', oscuro)],
        [('    return ', violeta), ('post', oscuro)],
    ]
    for i, partes in enumerate(lineas):
        lienzo.codigo(116, 250 + i * 40, partes, mono)

    lienzo.flecha(535, 300, 672, 300, BLANCO, ancho=8, punta=26)
    lienzo.texto(600, 270, 'POO', fuente(22, 'negrita'), BLANCO, anchor='mm')

    lienzo.tarjeta((700, 100, 1110, 500), 20, BLANCO)
    lienzo.rect((700, 100, 1110, 160), verde, radio=20, esquinas=(True, True, False, False))
    lienzo.texto(726, 130, 'class Post', fuente(26, 'negrita'), BLANCO, anchor='lm')
    mono = fuente(22, 'mono')
    for i, atributo in enumerate(['titulo: str', 'contenido: str', 'autor: User', 'estado: str']):
        y = 194 + i * 37
        lienzo.circulo(738, y, 6, (224, 112, 88))
        lienzo.texto(756, y, atributo, mono, oscuro, anchor='lm')
    lienzo.linea([(726, 345), (1084, 345)], (228, 228, 236), 3)
    for i, metodo in enumerate(['publicar()', 'archivar()', '__str__()']):
        y = 380 + i * 37
        lienzo.circulo(738, y, 6, verde)
        lienzo.texto(756, y, metodo, mono, oscuro, anchor='lm')
    return lienzo.archivo()


def ilustracion_django():
    """Datos en JSON y SQLite que terminan en una página web."""
    lienzo = Lienzo((9, 62, 43), (36, 128, 92))
    lienzo.manchas([
        (1060, 520, 210, (68, 183, 139, 150)),
        (140, 90, 150, (255, 255, 255, 45)),
        (700, 40, 120, (120, 220, 170, 70)),
    ])
    lienzo.puntos(1010, 30, 7, 2, color=(255, 255, 255, 50))

    _ventana(lienzo, (340, 80, 1110, 520), (246, 248, 247), (222, 229, 225))
    lienzo.rect((450, 94, 1000, 118), BLANCO, radio=12)
    lienzo.texto(468, 106, 'localhost:8000/posts/', fuente(16, 'mono'), (110, 120, 115), anchor='lm')

    lienzo.rect((340, 130, 1110, 172), (31, 58, 95))
    lienzo.texto(362, 151, 'Blog Web', fuente(17, 'negrita'), BLANCO, anchor='lm')
    for i in range(3):
        lienzo.rect((900 + i * 65, 146, 950 + i * 65, 156), (150, 170, 200), radio=5)

    lienzo.rect((370, 192, 1080, 262), (61, 90, 128), radio=12)
    lienzo.rect((395, 210, 700, 226), BLANCO, radio=8)
    lienzo.rect((395, 236, 600, 246), (180, 195, 220), radio=5)
    lienzo.rect((960, 214, 1050, 240), (224, 122, 95), radio=12)

    for i, color in enumerate([(224, 122, 95), (62, 145, 120), (61, 90, 128)]):
        x = 370 + i * 243
        lienzo.tarjeta((x, 282, x + 223, 500), 12, BLANCO, opacidad=40)
        lienzo.rect((x, 282, x + 223, 372), color, radio=12, esquinas=(True, True, False, False))
        for y0, largo in [(388, 174), (410, 134), (430, 154)]:
            lienzo.rect((x + 16, y0, x + 16 + largo, y0 + 10), (205, 211, 208), radio=5)
        lienzo.rect((x + 16, 460, x + 82, 484), (13, 110, 253), radio=6)

    lienzo.tarjeta((70, 140, 250, 290), 18, BLANCO)
    lienzo.texto(160, 198, '{ }', fuente(54, 'mono'), (12, 75, 51), anchor='mm')
    lienzo.texto(160, 258, 'datos.json', fuente(17, 'mono'), (90, 110, 100), anchor='mm')
    lienzo.flecha(262, 215, 326, 215, BLANCO, ancho=6, punta=18)

    lienzo.sombra((90, 340, 230, 490), 40, opacidad=70)
    lienzo.rect((90, 360, 230, 470), (68, 183, 139))
    lienzo.dibujo.ellipse(_e(90, 450, 230, 490), fill=(68, 183, 139))
    for y in (395, 430):
        lienzo.dibujo.arc(_e(90, y - 20, 230, y + 20), 0, 180, fill=(40, 140, 100), width=4 * ESCALA)
    lienzo.dibujo.ellipse(_e(90, 340, 230, 380), fill=(140, 220, 186))
    lienzo.texto(160, 518, 'SQLite', fuente(18, 'negrita'), BLANCO, anchor='mm')
    lienzo.flecha(262, 415, 326, 415, BLANCO, ancho=6, punta=18)
    return lienzo.archivo()


def ilustracion_ideas():
    """Lamparita rodeada de notas con ideas."""
    lienzo = Lienzo((58, 42, 120), (130, 84, 180))
    lienzo.manchas([
        (600, 250, 190, (255, 214, 102, 140)),
        (120, 520, 160, (255, 255, 255, 40)),
        (1100, 80, 150, (200, 160, 255, 90)),
    ], desenfoque=60)
    lienzo.puntos(530, 500, 7, 3, color=(255, 255, 255, 60))

    cx, cy, r = 600, 230, 105
    amarillo = (255, 214, 102)
    for grados in range(0, 181, 30):
        a = math.radians(grados)
        lienzo.linea(
            [(cx + 145 * math.cos(a), cy - 145 * math.sin(a)), (cx + 185 * math.cos(a), cy - 185 * math.sin(a))],
            (255, 226, 140), 9,
        )
    lienzo.circulo(cx, cy, r, amarillo)
    lienzo.dibujo.polygon(
        [tuple(_e(*p)) for p in [(cx - 62, cy + 78), (cx + 62, cy + 78), (cx + 48, cy + 130), (cx - 48, cy + 130)]],
        fill=amarillo,
    )
    lienzo.linea([(cx - 28, cy + 90), (cx - 28, cy + 20), (cx - 14, cy), (cx, cy + 20),
                  (cx + 14, cy), (cx + 28, cy + 20), (cx + 28, cy + 90)], (230, 150, 40), 6)
    lienzo.dibujo.ellipse(_e(cx - 72, cy - 72, cx - 38, cy - 22), fill=(255, 240, 190))
    lienzo.rect((cx - 52, cy + 128, cx + 52, cy + 182), (215, 215, 225), radio=10)
    for y in (cy + 146, cy + 164):
        lienzo.linea([(cx - 50, y), (cx + 50, y)], (170, 170, 185), 5)
    lienzo.rect((cx - 28, cy + 180, cx + 28, cy + 200), (150, 150, 165), radio=10)

    lienzo.nota(110, 60, 'Comentarios', (255, 236, 140), 8)
    lienzo.nota(90, 320, 'Categorías', (164, 228, 196), -6)
    lienzo.nota(850, 60, 'Buscador+', (255, 184, 196), -7)
    lienzo.nota(860, 320, 'Me gusta', (164, 206, 255), 6)
    return lienzo.archivo()
