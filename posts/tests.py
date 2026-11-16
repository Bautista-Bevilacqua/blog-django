import shutil
import tempfile
from io import BytesIO, StringIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post

MEDIA_TEMPORAL = tempfile.mkdtemp()
CLAVE = 'clave-segura-123'


def imagen_de_prueba(nombre='prueba.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, format='PNG')
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class PostTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def setUp(self):
        self.autor = User.objects.create_user('autor', password=CLAVE)
        self.otro = User.objects.create_user('otro', password=CLAVE)
        self.post = Post.objects.create(
            titulo='Primer post', contenido='Hola mundo Django', autor=self.autor, estado=Post.ESTADO_PUBLICADO,
        )

    def test_inicio_y_acerca(self):
        respuesta = self.client.get(reverse('posts:inicio'))
        self.assertContains(respuesta, 'Bienvenido/a')
        self.assertContains(respuesta, 'posts/css/estilos.css')
        self.assertContains(self.client.get(reverse('posts:acerca')), 'Sobre el autor')

    def test_lista_muestra_solo_publicados(self):
        Post.objects.create(titulo='Un borrador', contenido='x', autor=self.autor, estado=Post.ESTADO_BORRADOR)
        Post.objects.create(titulo='Un archivado', contenido='x', autor=self.autor, estado=Post.ESTADO_ARCHIVADO)
        respuesta = self.client.get(reverse('posts:lista'))
        self.assertContains(respuesta, 'Primer post')
        self.assertNotContains(respuesta, 'Un borrador')
        self.assertNotContains(respuesta, 'Un archivado')

    def test_anonimo_ve_detalle_sin_imagen(self):
        respuesta = self.client.get(reverse('posts:detalle', args=[self.post.pk]))
        self.assertContains(respuesta, 'Hola mundo Django')
        self.assertContains(respuesta, 'Publicado')
        self.assertContains(respuesta, 'Iniciar sesión')
        self.assertNotContains(respuesta, 'Editar')

    def test_borrador_solo_visible_para_el_autor(self):
        borrador = Post.objects.create(titulo='Borrador', contenido='x', autor=self.autor)
        url = reverse('posts:detalle', args=[borrador.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.login(username='autor', password=CLAVE)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_rutas_protegidas_redirigen_al_login(self):
        login_url = reverse('accounts:login')
        for url in [
            reverse('posts:crear'),
            reverse('posts:editar', args=[self.post.pk]),
            reverse('posts:eliminar', args=[self.post.pk]),
        ]:
            self.assertRedirects(self.client.get(url), f'{login_url}?next={url}')
        self.assertEqual(reverse('posts:crear'), '/crear/')

    def test_anonimo_no_puede_borrar_por_post(self):
        self.client.post(reverse('posts:eliminar', args=[self.post.pk]))
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_crear_post_con_imagen(self):
        self.client.login(username='autor', password=CLAVE)
        respuesta = self.client.post(reverse('posts:crear'), {
            'titulo': 'Con imagen',
            'contenido': 'Contenido',
            'estado': Post.ESTADO_PUBLICADO,
            'imagen': imagen_de_prueba(),
        })
        post = Post.objects.get(titulo='Con imagen')
        self.assertRedirects(respuesta, post.get_absolute_url())
        self.assertEqual(post.autor, self.autor)
        self.assertTrue(post.imagen.name.startswith('posts/'))
        self.assertContains(self.client.get(post.get_absolute_url()), post.imagen.url)

    def test_autor_edita_y_borra_con_confirmacion(self):
        self.client.login(username='autor', password=CLAVE)
        self.client.post(reverse('posts:editar', args=[self.post.pk]), {
            'titulo': 'Título editado',
            'contenido': 'Nuevo contenido',
            'estado': Post.ESTADO_ARCHIVADO,
            'imagen': imagen_de_prueba(),
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.titulo, 'Título editado')
        self.assertEqual(self.post.estado, Post.ESTADO_ARCHIVADO)
        self.assertTrue(self.post.imagen)

        url = reverse('posts:eliminar', args=[self.post.pk])
        self.assertContains(self.client.get(url), '¿Seguro que querés eliminar')
        self.assertRedirects(self.client.post(url), reverse('posts:lista'))
        self.assertFalse(Post.objects.exists())

    def test_otro_usuario_no_puede_editar_ni_borrar(self):
        self.client.login(username='otro', password=CLAVE)
        self.assertEqual(self.client.get(reverse('posts:editar', args=[self.post.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('posts:eliminar', args=[self.post.pk])).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_busqueda_por_titulo_y_contenido(self):
        Post.objects.create(titulo='Otro tema', contenido='Nada que ver', autor=self.autor, estado=Post.ESTADO_PUBLICADO)
        respuesta = self.client.get(reverse('posts:buscar'), {'q': 'primer'})
        self.assertContains(respuesta, 'Primer post')
        self.assertNotContains(respuesta, 'Otro tema')
        self.assertContains(self.client.get(reverse('posts:buscar'), {'q': 'django'}), 'Primer post')

    def test_busqueda_sin_resultados(self):
        respuesta = self.client.get(reverse('posts:buscar'), {'q': 'inexistente'})
        self.assertContains(respuesta, 'No se encontraron publicaciones')

    def test_comando_cargar_posts_ejemplo(self):
        User.objects.create_superuser('admin', 'admin@example.com', CLAVE)
        call_command('cargar_posts_ejemplo', stdout=StringIO())
        call_command('cargar_posts_ejemplo', stdout=StringIO())
        self.assertEqual(Post.objects.filter(autor__username='admin').count(), 4)
        self.assertEqual(Post.objects.filter(autor__username='admin', estado=Post.ESTADO_PUBLICADO).count(), 3)
        self.assertFalse(Post.objects.filter(autor__username='admin', imagen='').exists())
