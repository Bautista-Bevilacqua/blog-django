from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('acerca/', views.acerca, name='acerca'),
    path('posts/', views.lista_posts, name='lista'),
    path('posts/<int:pk>/', views.detalle_post, name='detalle'),
    path('crear/', views.crear_post, name='crear'),
    path('posts/<int:pk>/editar/', views.editar_post, name='editar'),
    path('posts/<int:pk>/eliminar/', views.eliminar_post, name='eliminar'),
    path('buscar/', views.buscar_posts, name='buscar'),
]
