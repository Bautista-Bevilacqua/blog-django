# Blog Web con Django

Blog web desarrollado con Django como proyecto final del curso de Python. Los visitantes pueden leer y buscar publicaciones. Los usuarios registrados además pueden escribir posts con imagen, editarlos, eliminarlos y gestionar su perfil.

## Tecnologías

- Python 3.12+ (desarrollado con 3.13)
- Django 6.1
- SQLite (base de datos por defecto de Django)
- Pillow (manejo de imágenes)
- python-decouple (variables de entorno)
- Bootstrap 5 (cargado por CDN)

## Funcionalidades

**Publicaciones**
- Listado de posts paginado, con la imagen o un recuadro "Sin imagen" si el post no tiene.
- Detalle de cada post.
- Crear, editar y eliminar posts desde la interfaz web, sin pasar por el admin.
- Subida de imagen opcional por post.
- Solo el autor (o un superusuario) puede editar o eliminar su post.

**Usuarios**
- Registro, inicio de sesión y cierre de sesión.
- Perfil con nombre, email, biografía, imagen de perfil y listado de posts propios.
- Edición del perfil y del avatar.
- La barra de navegación cambia según el visitante sea anónimo o tenga sesión iniciada.

**Rutas protegidas**
- Crear, editar y eliminar posts usan `LoginRequiredMixin`; ver y editar el perfil usan `@login_required`.
- Un visitante anónimo que entra a esas URLs es redirigido al login.

**Búsqueda**
- Busca por título o contenido desde la barra de navegación (`/buscar/?q=...`).
- Muestra los resultados o avisa cuando no hay coincidencias.

## Estructura

```
├── config/            # Configuración del proyecto (settings, urls)
├── posts/             # App de publicaciones: modelo, vistas CRUD, búsqueda, templates
├── accounts/          # App de usuarios: registro, login/logout, perfil
├── templates/         # Template base compartido (base.html)
├── static/css/        # Estilos propios
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

Windows (PowerShell):

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

Copiá `.env.example` como `.env`:

```bash
cp .env.example .env
```

En Windows con `cmd` se usa `copy .env.example .env`.

Después reemplazá `SECRET_KEY` por una clave propia. Podés generar una con:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable        | Descripción                                        | Ejemplo               |
|-----------------|----------------------------------------------------|-----------------------|
| `SECRET_KEY`    | Clave secreta de Django (obligatoria)              | `una-clave-larga`     |
| `DEBUG`         | Modo debug. Tiene que estar en `True` para que se vean las imágenes en desarrollo | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma               | `127.0.0.1,localhost` |

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. (Opcional) Crear un superusuario para el panel de administración

```bash
python manage.py createsuperuser
```

El admin está en http://127.0.0.1:8000/admin/

### 7. Iniciar el servidor

```bash
python manage.py runserver
```

Abrí http://127.0.0.1:8000/ en el navegador.

## Probar el proyecto desde cero

El repositorio **no incluye** `db.sqlite3` ni la carpeta `media/`, así que el evaluador arranca con una base limpia:

1. `python manage.py migrate` crea la base de datos vacía.
2. Entrá a **Registrarse** y creá un usuario. Al registrarte, la sesión queda iniciada.
3. Usá **Nuevo post** para crear publicaciones, con imagen y sin imagen. La carpeta `media/` se crea sola al subir la primera imagen.
4. Probá editar y eliminar desde el detalle del post, buscar desde la barra superior y editar el perfil.
5. Cerrá sesión e intentá entrar a `/posts/nuevo/` o `/accounts/perfil/`: te va a redirigir al login.

### Tests automáticos

El proyecto incluye tests de CRUD, imágenes, búsqueda, registro, login, logout y rutas protegidas:

```bash
python manage.py test
```

## URLs principales

| URL                          | Descripción                    | Requiere login |
|------------------------------|--------------------------------|----------------|
| `/`                          | Listado de posts               | No             |
| `/posts/<id>/`               | Detalle de un post             | No             |
| `/buscar/?q=texto`           | Búsqueda                       | No             |
| `/posts/nuevo/`              | Crear post                     | Sí             |
| `/posts/<id>/editar/`        | Editar post (solo el autor)    | Sí             |
| `/posts/<id>/eliminar/`      | Eliminar post (solo el autor)  | Sí             |
| `/accounts/registro/`        | Registro                       | No             |
| `/accounts/login/`           | Iniciar sesión                 | No             |
| `/accounts/perfil/`          | Ver perfil                     | Sí             |
| `/accounts/perfil/editar/`   | Editar perfil                  | Sí             |

## Autor

**Bautista Bevilacqua**. GitHub: [@Bautista-Bevilacqua](https://github.com/Bautista-Bevilacqua)
