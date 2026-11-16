from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class AccountsTests(TestCase):
    def test_signup_creates_user_profile_and_logs_in(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'nuevo',
            'email': 'nuevo@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'unaClaveLarga123',
            'password2': 'unaClaveLarga123',
        })
        self.assertRedirects(response, reverse('posts:list'))
        user = User.objects.get(username='nuevo')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_login_and_logout(self):
        User.objects.create_user('ana', password='clave-segura-123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'ana',
            'password': 'clave-segura-123',
        })
        self.assertRedirects(response, reverse('posts:list'))
        self.assertContains(self.client.get(reverse('posts:list')), 'Hola, ana')

        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('posts:list'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_profile_routes_require_login(self):
        login_url = reverse('accounts:login')
        for url in [reverse('accounts:profile'), reverse('accounts:profile_edit')]:
            self.assertRedirects(self.client.get(url), f'{login_url}?next={url}')

    def test_edit_profile(self):
        User.objects.create_user('ana', password='clave-segura-123')
        self.client.login(username='ana', password='clave-segura-123')
        response = self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Ana',
            'last_name': 'García',
            'email': 'ana@example.com',
            'bio': 'Me gusta escribir.',
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.assertContains(self.client.get(reverse('accounts:profile')), 'Me gusta escribir.')
