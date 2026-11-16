import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Perfil

MEDIA_TEMPORAL = tempfile.mkdtemp()
CLAVE = 'clave-segura-123'


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class AccountsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def test_registro_crea_usuario_con_perfil_e_inicia_sesion(self):
        respuesta = self.client.post(reverse('accounts:registro'), {
            'username': 'nuevo',
            'email': 'nuevo@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'unaClaveLarga123',
            'password2': 'unaClaveLarga123',
        })
        self.assertRedirects(respuesta, reverse('posts:inicio'))
        usuario = User.objects.get(username='nuevo')
        self.assertTrue(Perfil.objects.filter(usuario=usuario).exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_menu_segun_sesion(self):
        respuesta = self.client.get(reverse('posts:inicio'))
        self.assertContains(respuesta, 'Iniciar sesión')
        self.assertContains(respuesta, 'Registrarse')
        self.assertNotContains(respuesta, 'Mi perfil')

        User.objects.create_user('ana', password=CLAVE)
        self.client.login(username='ana', password=CLAVE)
        respuesta = self.client.get(reverse('posts:inicio'))
        for texto in ['Mi perfil', 'Crear post', 'Cerrar sesión']:
            self.assertContains(respuesta, texto)
        self.assertNotContains(respuesta, 'Registrarse')

    def test_login_y_logout(self):
        User.objects.create_user('ana', password=CLAVE)
        respuesta = self.client.post(reverse('accounts:login'), {'username': 'ana', 'password': CLAVE})
        self.assertRedirects(respuesta, reverse('posts:inicio'))
        self.assertIn('_auth_user_id', self.client.session)

        respuesta = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(respuesta, reverse('posts:inicio'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_perfil_requiere_login(self):
        login_url = reverse('accounts:login')
        for url in [reverse('accounts:perfil'), reverse('accounts:editar_perfil')]:
            self.assertRedirects(self.client.get(url), f'{login_url}?next={url}')

    def test_editar_perfil_con_avatar(self):
        User.objects.create_user('ana', password=CLAVE)
        self.client.login(username='ana', password=CLAVE)
        buffer = BytesIO()
        Image.new('RGB', (10, 10), 'blue').save(buffer, format='PNG')
        avatar = SimpleUploadedFile('avatar.png', buffer.getvalue(), content_type='image/png')

        respuesta = self.client.post(reverse('accounts:editar_perfil'), {
            'first_name': 'Ana',
            'last_name': 'García',
            'email': 'ana@example.com',
            'biografia': 'Me gusta escribir.',
            'avatar': avatar,
        })
        self.assertRedirects(respuesta, reverse('accounts:perfil'))
        perfil = Perfil.objects.get(usuario__username='ana')
        self.assertTrue(perfil.avatar.name.startswith('avatars/'))

        respuesta = self.client.get(reverse('accounts:perfil'))
        self.assertContains(respuesta, 'Me gusta escribir.')
        self.assertContains(respuesta, 'ana@example.com')
        self.assertContains(respuesta, perfil.avatar.url)
