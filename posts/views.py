from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PostForm
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.select_related('author')


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post publicado correctamente.')
        return super().form_valid(form)


class AuthorRequiredMixin(UserPassesTestMixin):
    """Solo el autor del post (o un superusuario) puede modificarlo."""

    def test_func(self):
        post = self.get_object()
        user = self.request.user
        return user == post.author or user.is_superuser


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Post actualizado correctamente.')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('posts:list')

    def form_valid(self, form):
        messages.success(self.request, 'Post eliminado.')
        return super().form_valid(form)
