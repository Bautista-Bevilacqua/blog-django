from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageDraw, ImageFont

from posts.models import Post

POSTS_EJEMPLO = [
    {
        'titulo': 'Mis primeros pasos con Python',
        'contenido': (
            'Empecé el curso escribiendo instrucciones simples en la consola: variables, listas y diccionarios.\n\n'
            'Al principio parecía poco, pero esas bases son las que después sostienen todo el proyecto.'
        ),
        'estado': Post.ESTADO_PUBLICADO,
        'colores': ((31, 58, 95), (61, 90, 128)),
    },
    {
        'titulo': 'De funciones a clases',
        'contenido': (
            'Organizar el código en funciones y módulos lo hizo mucho más legible. '
            'Con la Programación Orientada a Objetos cada concepto pasó a tener su propia clase.'
        ),
        'estado': Post.ESTADO_PUBLICADO,
        'colores': ((224, 122, 95), (242, 204, 143)),
    },
    {
        'titulo': 'El salto a Django',
        'contenido': (
            'Pasar de guardar datos en JSON a usar modelos de Django y una base de datos fue el gran cambio. '
            'Con el admin, los formularios y las vistas, el blog se convirtió en una aplicación web real.'
        ),
        'estado': Post.ESTADO_PUBLICADO,
        'colores': ((12, 75, 51), (68, 183, 139)),
    },
    {
        'titulo': 'Ideas para próximas mejoras',
        'contenido': 'Comentarios, categorías y un buscador más completo. Este post está en borrador.',
        'estado': Post.ESTADO_BORRADOR,
        'colores': ((90, 90, 110), (160, 160, 180)),
    },
]


def generar_imagen(titulo, colores, ancho=1200, alto=600):
    """Genera una imagen PNG con un degradado y el título del post."""
    inicio, fin = colores
    imagen = Image.new('RGB', (ancho, alto))
    dibujo = ImageDraw.Draw(imagen)
    for x in range(ancho):
        t = x / (ancho - 1)
        color = tuple(int(inicio[i] + (fin[i] - inicio[i]) * t) for i in range(3))
        dibujo.line([(x, 0), (x, alto)], fill=color)

    tamanio = 72
    fuente = ImageFont.load_default(size=tamanio)
    caja = dibujo.textbbox((0, 0), titulo, font=fuente)
    while caja[2] - caja[0] > ancho * 0.65 and tamanio > 20:
        tamanio -= 4
        fuente = ImageFont.load_default(size=tamanio)
        caja = dibujo.textbbox((0, 0), titulo, font=fuente)
    posicion = ((ancho - (caja[2] - caja[0])) / 2, (alto - (caja[3] - caja[1])) / 2)
    dibujo.text(posicion, titulo, font=fuente, fill='white')

    buffer = BytesIO()
    imagen.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = 'Carga posts de ejemplo con imagen para probar el blog. Usa el primer superusuario como autor.'

    def add_arguments(self, parser):
        parser.add_argument('--usuario', help='Nombre de usuario que figurará como autor de los posts.')

    def handle(self, *args, **options):
        User = get_user_model()
        if options['usuario']:
            autor = User.objects.filter(username=options['usuario']).first()
            if autor is None:
                raise CommandError(f'No existe el usuario "{options["usuario"]}".')
        else:
            autor = User.objects.filter(is_superuser=True).order_by('pk').first()
            if autor is None:
                raise CommandError(
                    'No hay superusuarios. Creá uno con "python manage.py createsuperuser" '
                    'o indicá un usuario con --usuario.'
                )

        creados = 0
        for indice, datos in enumerate(POSTS_EJEMPLO, start=1):
            campos = {k: v for k, v in datos.items() if k != 'colores'}
            post, creado = Post.objects.get_or_create(titulo=datos['titulo'], autor=autor, defaults=campos)
            creados += creado
            if not post.imagen:
                post.imagen.save(f'ejemplo_{indice}.png', generar_imagen(datos['titulo'], datos['colores']))

        self.stdout.write(self.style.SUCCESS(f'Se cargaron {creados} posts de ejemplo con autor "{autor.username}".'))
