from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Post


def _posts_publicados():
    return Post.objects.filter(estado=Post.ESTADO_PUBLICADO).order_by('-fecha_creacion').select_related('autor')


def _puede_modificar(user, post):
    return user == post.autor or user.is_superuser


def _obtener_post_editable(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not _puede_modificar(request.user, post):
        raise PermissionDenied('Solo el autor puede modificar este post.')
    return post


def inicio(request):
    return render(request, 'posts/inicio.html', {'ultimos_posts': _posts_publicados()[:3]})


def acerca(request):
    return render(request, 'posts/acerca.html')


def lista_posts(request):
    paginador = Paginator(_posts_publicados(), 6)
    pagina = paginador.get_page(request.GET.get('page'))
    return render(request, 'posts/lista_posts.html', {'posts': pagina, 'pagina': pagina})


def detalle_post(request, pk):
    post = get_object_or_404(Post.objects.select_related('autor'), pk=pk)
    # Los borradores y archivados solo los ve su autor.
    if post.estado != Post.ESTADO_PUBLICADO and not _puede_modificar(request.user, post):
        raise Http404('Post no disponible.')
    return render(request, 'posts/detalle_post.html', {
        'post': post,
        'puede_modificar': _puede_modificar(request.user, post),
    })


def buscar_posts(request):
    consulta = request.GET.get('q', '').strip()
    posts = []
    if consulta:
        posts = _posts_publicados().filter(Q(titulo__icontains=consulta) | Q(contenido__icontains=consulta))
    return render(request, 'posts/buscar_posts.html', {'posts': posts, 'consulta': consulta})


@login_required
def crear_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, 'Post creado correctamente.')
            return redirect(post)
    else:
        form = PostForm(initial={'estado': Post.ESTADO_PUBLICADO})
    return render(request, 'posts/post_form.html', {'form': form})


@login_required
def editar_post(request, pk):
    post = _obtener_post_editable(request, pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post actualizado correctamente.')
            return redirect(post)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'form': form, 'post': post})


@login_required
def eliminar_post(request, pk):
    post = _obtener_post_editable(request, pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post eliminado.')
        return redirect('posts:lista')
    return render(request, 'posts/confirmar_eliminar.html', {'post': post})
