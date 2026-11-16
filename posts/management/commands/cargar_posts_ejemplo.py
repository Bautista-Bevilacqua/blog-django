from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from posts.models import Post

from ._ilustraciones import ilustracion_django, ilustracion_ideas, ilustracion_poo, ilustracion_python

POSTS_EJEMPLO = [
    {
        'titulo': 'Mis primeros pasos con Python',
        'contenido': (
            'Empecé el curso escribiendo instrucciones simples en la consola: variables, listas y diccionarios.\n\n'
            'Al principio parecía poco, pero esas bases son las que después sostienen todo el proyecto.'
        ),
        'estado': Post.ESTADO_PUBLICADO,
        'ilustracion': ilustracion_python,
    },
    {
        'titulo': 'De funciones a clases',
        'contenido': (
            'Organizar el código en funciones y módulos lo hizo mucho más legible. '
            'Con la Programación Orientada a Objetos cada concepto pasó a tener su propia clase.'
        ),
        'estado': Post.ESTADO_PUBLICADO,
        'ilustracion': ilustracion_poo,
    },
    {
        'titulo': 'El salto a Django',
        'contenido': (
            'Pasar de guardar datos en JSON a usar modelos de Django y una base de datos fue el gran cambio. '
            'Con el admin, los formularios y las vistas, el blog se convirtió en una aplicación web real.'
        ),
        'estado': Post.ESTADO_PUBLICADO,
        'ilustracion': ilustracion_django,
    },
    {
        'titulo': 'Ideas para próximas mejoras',
        'contenido': 'Comentarios, categorías y un buscador más completo. Este post está en borrador.',
        'estado': Post.ESTADO_BORRADOR,
        'ilustracion': ilustracion_ideas,
    },
]


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
            campos = {k: v for k, v in datos.items() if k != 'ilustracion'}
            post, creado = Post.objects.get_or_create(titulo=datos['titulo'], autor=autor, defaults=campos)
            creados += creado
            if not post.imagen:
                post.imagen.save(f'ejemplo_{indice}.png', datos['ilustracion']())

        self.stdout.write(self.style.SUCCESS(f'Se cargaron {creados} posts de ejemplo con autor "{autor.username}".'))
