from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil


def _aplicar_bootstrap(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault('class', 'form-control')


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_bootstrap(self)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_bootstrap(self)


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_bootstrap(self)


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ('biografia', 'avatar')
        widgets = {'biografia': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_bootstrap(self)
