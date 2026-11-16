import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Post

TEMP_MEDIA = tempfile.mkdtemp()


def fake_image(name='test.png'):
    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PostViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.author = User.objects.create_user('autor', password='clave-segura-123')
        self.other = User.objects.create_user('otro', password='clave-segura-123')
        self.post = Post.objects.create(title='Primer post', content='Hola mundo Django', author=self.author)

    def test_anonymous_can_list_and_view_detail(self):
        self.assertContains(self.client.get(reverse('posts:list')), 'Primer post')
        response = self.client.get(reverse('posts:detail', args=[self.post.pk]))
        self.assertContains(response, 'Hola mundo Django')
        self.assertContains(response, 'Iniciar sesión')

    def test_detail_without_image_renders(self):
        response = self.client.get(reverse('posts:detail', args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)

    def test_protected_routes_redirect_anonymous_to_login(self):
        login_url = reverse('accounts:login')
        for url in [
            reverse('posts:create'),
            reverse('posts:update', args=[self.post.pk]),
            reverse('posts:delete', args=[self.post.pk]),
        ]:
            response = self.client.get(url)
            self.assertRedirects(response, f'{login_url}?next={url}')

    def test_anonymous_post_to_delete_does_not_delete(self):
        self.client.post(reverse('posts:delete', args=[self.post.pk]))
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_create_post_with_image(self):
        self.client.login(username='autor', password='clave-segura-123')
        response = self.client.post(reverse('posts:create'), {
            'title': 'Con imagen',
            'content': 'Contenido',
            'image': fake_image(),
        })
        post = Post.objects.get(title='Con imagen')
        self.assertRedirects(response, post.get_absolute_url())
        self.assertEqual(post.author, self.author)
        self.assertTrue(post.image.name.startswith('posts/'))
        self.assertContains(self.client.get(post.get_absolute_url()), post.image.url)

    def test_author_can_edit_and_delete(self):
        self.client.login(username='autor', password='clave-segura-123')
        self.client.post(reverse('posts:update', args=[self.post.pk]), {
            'title': 'Título editado',
            'content': 'Nuevo contenido',
        })
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Título editado')

        response = self.client.post(reverse('posts:delete', args=[self.post.pk]))
        self.assertRedirects(response, reverse('posts:list'))
        self.assertFalse(Post.objects.exists())

    def test_other_user_cannot_edit_or_delete(self):
        self.client.login(username='otro', password='clave-segura-123')
        self.assertEqual(self.client.get(reverse('posts:update', args=[self.post.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('posts:delete', args=[self.post.pk])).status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_search_by_title_and_content(self):
        Post.objects.create(title='Otro tema', content='Nada que ver', author=self.author)
        response = self.client.get(reverse('posts:search'), {'q': 'primer'})
        self.assertContains(response, 'Primer post')
        self.assertNotContains(response, 'Otro tema')

        response = self.client.get(reverse('posts:search'), {'q': 'django'})
        self.assertContains(response, 'Primer post')

    def test_search_without_results(self):
        response = self.client.get(reverse('posts:search'), {'q': 'inexistente'})
        self.assertContains(response, 'No se encontraron publicaciones')
