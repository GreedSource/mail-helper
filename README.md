# greedsource-mail-helper

Librería reutilizable para enviar correo SMTP y renderizar plantillas Jinja2. No depende directamente de Flask ni FastAPI: ambos frameworks son opcionales y se puede usar la misma API desde cualquier aplicación Python.

## Instalación

Con acceso SSH al repositorio privado de GitHub:

```bash
pip install "greedsource-mail-helper @ git+ssh://git@github.com/GreedSource/mail-helper.git@main"
```

Para Bitbucket, reemplaza `workspace` por el workspace propietario del repositorio:

```bash
pip install "greedsource-mail-helper @ git+ssh://git@bitbucket.org/workspace/mail-helper.git@main"
```

También se puede instalar con un token HTTPS configurado mediante Git Credential Manager. Evita guardar tokens directamente en `requirements.txt` o en la URL del comando.

## Desarrollo y calidad del código

Instala las herramientas de desarrollo y configura el hook local de pre-commit:

```bash
pip install -e ".[dev]"
pre-commit install
```

En cada commit, Ruff revisa los errores comunes, los imports y las actualizaciones de sintaxis; también aplica formato. Para ejecutar las comprobaciones manualmente:

```bash
pre-commit run --all-files
pytest
```

GitHub Actions ejecuta estas comprobaciones y las pruebas en cada push de cualquier rama y en todos los pull requests. Ruff no corrige automáticamente en el hook: si encuentra errores de lint o formato, el commit local y el workflow fallan hasta corregirlos.

Instala el extra del framework si tu aplicación necesita ese framework:

```bash
pip install "greedsource-mail-helper[flask] @ git+ssh://git@github.com/GreedSource/mail-helper.git@main"
pip install "greedsource-mail-helper[fastapi] @ git+ssh://git@github.com/GreedSource/mail-helper.git@main"
```

## Configuración

`MailHelper` lee estas variables de entorno cuando se llama `init_app()` sin configuración explícita:

| Variable | Predeterminado | Descripción |
|---|---:|---|
| `MAIL_SERVER` | requerido | Host SMTP |
| `MAIL_PORT` | `587` | Puerto SMTP |
| `MAIL_USERNAME` | — | Usuario SMTP (opcional) |
| `MAIL_PASSWORD` | — | Contraseña SMTP (opcional) |
| `MAIL_DEFAULT_SENDER` | — | Remitente predeterminado |
| `MAIL_USE_TLS` | `true` | Habilita STARTTLS |
| `MAIL_USE_SSL` | `false` | Usa SMTP sobre SSL; desactiva STARTTLS |
| `MAIL_TIMEOUT` | `30` | Timeout en segundos |

El remitente puede definirse por mensaje o con `MAIL_DEFAULT_SENDER`. No incluyas credenciales en el código fuente.

## Flask

```python
from flask import Flask
from mail_helper import MailHelper, TemplateHelper

app = Flask(__name__)
app.config.update(
    MAIL_SERVER="smtp.example.com",
    MAIL_PORT=587,
    MAIL_USERNAME="user",
    MAIL_PASSWORD="secret",
    MAIL_DEFAULT_SENDER="noreply@example.com",
)

mail = MailHelper().init_app(app)
templates = TemplateHelper().init_app(app, globals={"app_name": "Mi aplicación"})

mail.send_email(
    subject="Bienvenido",
    recipients=["persona@example.com"],
    body="Gracias por registrarte.",
    html="<h1>Bienvenido</h1>",
)
html = templates.render("welcome.html", {"name": "Ada"})
```

Flask guarda las instancias en `app.extensions["mail_helper"]` y `app.extensions["template_helper"]`. Para plantillas personalizadas, inicializa `TemplateHelper(template_folder="ruta/a/templates")` sin pasar `app`, o usa el directorio de plantillas configurado por Flask al pasar `app`.

## FastAPI

```python
from fastapi import BackgroundTasks, FastAPI
from mail_helper import MailHelper, TemplateHelper

app = FastAPI()
mail = MailHelper().init_app()  # Lee la configuración del entorno
templates = TemplateHelper(template_folder="templates")
mail.init_app(app)
templates.init_app(app)


@app.post("/welcome")
def send_welcome(background_tasks: BackgroundTasks):
    mail.send_email(
        subject="Bienvenido",
        recipients=["persona@example.com"],
        html=templates.render("welcome.html", {"name": "Ada"}),
        background_tasks=background_tasks,
    )
    return {"queued": True}
```

FastAPI dispone las instancias en `app.state.mail_helper` y `app.state.template_helper`. `background_tasks` es opcional; sin él, el envío es síncrono.

## API

- `MailConfig(...)`: configuración SMTP explícita y tipada.
- `MailHelper(config=None).init_app(app=None, config=None)`: inicializa con la configuración del framework, del entorno o una instancia `MailConfig`.
- `MailHelper.send_email(subject, recipients, body=None, html=None, sender=None, background_tasks=None)`: devuelve `True` si se envía o agenda correctamente, `False` si SMTP falla.
- `TemplateHelper(template_folder="templates", globals=None).render(template_name, context=None, **kwargs)`: renderiza un template Jinja2 con autoescape para HTML/XML.
