from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='usuario',
    )
    avatar = models.ImageField('imagen de perfil', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('biografía', max_length=500, blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'

    def __str__(self):
        return f'Perfil de {self.user.username}'
