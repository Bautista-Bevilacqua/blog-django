from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Formulario de posts. El autor no se elige: es el usuario con sesión iniciada."""

    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'estado', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
