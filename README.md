# Blog Web con Django

Blog web desarrollado con Django como proyecto final del curso de Python. Los visitantes pueden leer y buscar las publicaciones. Los usuarios registrados además pueden escribir posts con imagen, elegir si quedan en borrador, publicados o archivados, editarlos, eliminarlos y gestionar su perfil con avatar y biografía.

## Tecnologías

- Python 3.12+ (desarrollado con 3.13)
- Django 6.1
- SQLite (base de datos por defecto de Django)
- Pillow (manejo de imágenes)
- python-decouple (variables de entorno)
- Bootstrap 5 (cargado por CDN), junto con estilos propios en `posts/static/posts/css/estilos.css`

## Funcionalidades

**Páginas generales**
- **Inicio** (`inicio.html`): bienvenida y últimas publicaciones.
- **Acerca** (`acerca.html`): propósito del sitio y reseña del autor.

**Publicaciones (app `posts`)**
- Modelo `Post` con `titulo`, `contenido`, `autor`, `fecha_creacion`, `estado` e `imagen`. El estado puede ser borrador, publicado o archivado.
- El listado muestra solo los posts publicados, del más nuevo al más viejo.
- El detalle muestra título, contenido, autor, estado e imagen. Los borradores y archivados solo los ve su autor.
- Crear, editar y eliminar desde la interfaz web, sin pasar por el admin. Antes de borrar se pide confirmación.
- La imagen es opcional y se muestra solo si existe, así que un post sin imagen no rompe el template.
- Solo el autor (o un superusuario) puede editar o eliminar su post.
- Búsqueda por título o contenido. Si no hay coincidencias, se avisa.
- Admin con `PostAdmin`, que muestra título, autor, estado y fecha.

**Usuarios (app `accounts`)**
- Registro con un formulario propio basado en `UserCreationForm`.
- Inicio y cierre de sesión con las vistas nativas de Django.
- Modelo `Perfil` (`OneToOneField` a `User`) con `biografia` y `avatar`. Se crea automáticamente al registrarse.
- Página **Mi perfil** con usuario, email, biografía, avatar y los posts propios.
- Edición de nombre, email, biografía y avatar.
- El menú cambia según la sesión:
  - Sin sesión: *Iniciar sesión* y *Registrarse*.
  - Con sesión: *Mi perfil*, *Crear post* y *Cerrar sesión*.

**Rutas protegidas**
- Crear, editar y eliminar posts, *Mi perfil* y la edición del perfil usan `@login_required`. Si un visitante anónimo entra a esas URLs, lo redirige al login.
- El inicio, el listado, el detalle de posts publicados, la búsqueda y la página Acerca son públicos.

## Estructura

```
├── blog_project/                  # Configuración del proyecto (settings, urls)
├── posts/
│   ├── models.py, views.py, forms.py, urls.py, admin.py
│   ├── management/commands/       # Comando cargar_posts_ejemplo
│   ├── templates/posts/           # base.html, inicio, acerca, listado, detalle, formulario...
│   └── static/posts/css/          # estilos.css
├── accounts/
│   ├── models.py (Perfil), views.py, forms.py, urls.py, admin.py
│   └── templates/accounts/        # login, registro, perfil, editar_perfil
├── requirements.txt
├── .env.example
└── manage.py
```

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/Bautista-Bevilacqua/blog-django.git
cd blog-django
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
```

Windows (PowerShell o cmd):

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiá `.env.example` como `.env`. En Windows con `cmd` se usa `copy .env.example .env`:

```bash
cp .env.example .env
```

Después reemplazá `SECRET_KEY` por una clave propia. Podés generar una con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable        | Descripción                                                               | Ejemplo               |
|-----------------|---------------------------------------------------------------------------|-----------------------|
| `SECRET_KEY`    | Clave secreta de Django (obligatoria)                                     | `una-clave-larga`     |
| `DEBUG`         | Modo debug. Tiene que estar en `True` para que se vean las imágenes en desarrollo | `True`        |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma                                      | `127.0.0.1,localhost` |

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear un superusuario (para el panel de administración)

```bash
python manage.py createsuperuser
```

El admin está en http://127.0.0.1:8000/admin/

### 7. (Opcional) Cargar posts de ejemplo

Este comando crea 3 posts publicados y 1 borrador, cada uno con una imagen de ejemplo generada automáticamente. Usa al primer superusuario como autor:

```bash
python manage.py cargar_posts_ejemplo
```

También se puede elegir otro autor con `--usuario nombre_de_usuario`. Otra opción es cargar los posts a mano desde `/admin/`.

### 8. Iniciar el servidor

```bash
python manage.py runserver
```

Abrí http://127.0.0.1:8000/ en el navegador.

## Probar el proyecto desde cero

El repositorio **no incluye** `db.sqlite3` ni la carpeta `media/`, así que se arranca con una base limpia. Después de los pasos 1 a 8:

1. Entrá a **Registrarse** y creá un usuario. Al registrarte, la sesión queda iniciada.
2. En **Mi perfil**, tocá *Editar perfil* y cargá una biografía y un avatar.
3. Con **Crear post** escribí un post con imagen y otro sin imagen. La carpeta `media/` se crea sola al subir la primera imagen.
4. Desde el detalle del post, probá *Editar* y *Eliminar*. Para borrar te va a pedir confirmación.
5. Probá el buscador de la barra superior.
6. Cerrá sesión y entrá por URL a http://127.0.0.1:8000/crear/. Te va a redirigir al login.

### Tests automáticos

Hay tests para el CRUD, las imágenes, los estados, la búsqueda, el registro, el login y logout, el perfil y las rutas protegidas:

```bash
python manage.py test
```

## URLs principales

| URL                          | Descripción                        | Requiere login |
|------------------------------|------------------------------------|----------------|
| `/`                          | Inicio                             | No             |
| `/acerca/`                   | Acerca del sitio y del autor       | No             |
| `/posts/`                    | Listado de posts publicados        | No             |
| `/posts/<id>/`               | Detalle de un post                 | No             |
| `/buscar/?q=texto`           | Búsqueda                           | No             |
| `/crear/`                    | Crear post                         | Sí             |
| `/posts/<id>/editar/`        | Editar post (solo el autor)        | Sí             |
| `/posts/<id>/eliminar/`      | Eliminar post (solo el autor)      | Sí             |
| `/accounts/registro/`        | Registro                           | No             |
| `/accounts/login/`           | Iniciar sesión                     | No             |
| `/accounts/perfil/`          | Mi perfil                          | Sí             |
| `/accounts/perfil/editar/`   | Editar perfil                      | Sí             |
| `/admin/`                    | Panel de administración            | Superusuario   |

## Decisiones de diseño

- **El autor no se elige en el formulario.** Al crear un post, el autor es el usuario que tiene la sesión iniciada. Así nadie puede publicar a nombre de otro. Desde el admin sí se puede asignar cualquier autor.
- **Vistas basadas en funciones** con `render()`. Las de crear, editar y editar perfil procesan `request.FILES`.

## Autor

**Bautista Bevilacqua**. GitHub: [@Bautista-Bevilacqua](https://github.com/Bautista-Bevilacqua)
