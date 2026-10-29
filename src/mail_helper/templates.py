from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateHelper:
    """Render Jinja templates from a configurable filesystem directory."""

    def __init__(
        self,
        template_folder: str = "templates",
        globals: Mapping[str, Any] | None = None,
    ) -> None:
        self.env: Environment | None = None
        self.template_folder = template_folder
        self.init_app(template_folder=template_folder, globals=globals)

    def init_app(
        self,
        app: Any = None,
        template_folder: str | None = None,
        globals: Mapping[str, Any] | None = None,
    ) -> TemplateHelper:
        if app is not None and hasattr(app, "jinja_env"):
            self.env = app.jinja_env
        else:
            if template_folder is not None:
                self.template_folder = template_folder
            self.env = Environment(
                loader=FileSystemLoader(str(Path(self.template_folder))),
                autoescape=select_autoescape(["html", "xml"]),
            )

        for name, value in {
            "app_name": "",
            "frontend_url": "",
            "company_name": "Mi Empresa",
            "logo_url": "",
            "now": datetime.now,
        }.items():
            self.env.globals.setdefault(name, value)
        if globals:
            self.env.globals.update(globals)

        if app is not None:
            extensions = getattr(app, "extensions", None)
            if isinstance(extensions, dict):
                extensions["template_helper"] = self
            state = getattr(app, "state", None)
            if state is not None:
                state.template_helper = self
        return self

    def render(
        self,
        template_name: str,
        context: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        if self.env is None:
            raise RuntimeError(
                "TemplateHelper is not initialized; call init_app() first"
            )
        values = dict(context or {})
        values.update(kwargs)
        return self.env.get_template(template_name).render(**values)
