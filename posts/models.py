from django.conf import settings
from django.db import models
from django.urls import reverse


class Post(models.Model):
    ESTADO_BORRADOR = 'borrador'
    ESTADO_PUBLICADO = 'publicado'
    ESTADO_ARCHIVADO = 'archivado'
    ESTADOS = [
        (ESTADO_BORRADOR, 'Borrador'),
        (ESTADO_PUBLICADO, 'Publicado'),
        (ESTADO_ARCHIVADO, 'Archivado'),
    ]

    titulo = models.CharField('título', max_length=200)
    contenido = models.TextField('contenido')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='autor',
    )
    fecha_creacion = models.DateTimeField('fecha de creación', auto_now_add=True)
    estado = models.CharField('estado', max_length=10, choices=ESTADOS, default=ESTADO_BORRADOR)
    imagen = models.ImageField('imagen', upload_to='posts/', null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('posts:detalle', args=[self.pk])
