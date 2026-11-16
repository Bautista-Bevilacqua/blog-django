from django.conf import settings
from django.db import models
from django.urls import reverse


class Post(models.Model):
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('subtítulo', max_length=250, blank=True)
    content = models.TextField('contenido')
    image = models.ImageField('imagen', upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='autor',
    )
    created_at = models.DateTimeField('creado', auto_now_add=True)
    updated_at = models.DateTimeField('actualizado', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.pk])
