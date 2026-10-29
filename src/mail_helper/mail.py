import logging
import smtplib
from email.message import EmailMessage
from typing import Any, Mapping, Optional, Sequence

from .config import MailConfig

logger = logging.getLogger(__name__)


class MailHelper:
    """Send email through SMTP, with no required Flask or FastAPI dependency."""

    def __init__(self, config: Optional[MailConfig] = None) -> None:
        self.config = config

    def init_app(
        self,
        app: Any = None,
        config: Optional[MailConfig] = None,
    ) -> "MailHelper":
        if config is not None:
            self.config = config
        elif app is not None:
            app_config = getattr(app, "config", None)
            if isinstance(app_config, Mapping) and app_config.get("MAIL_SERVER"):
                self.config = _config_from_mapping(app_config)
            else:
                self.config = MailConfig.from_env()
        elif self.config is None:
            self.config = MailConfig.from_env()

        if app is not None:
            extensions = getattr(app, "extensions", None)
            if isinstance(extensions, dict):
                extensions["mail_helper"] = self
            state = getattr(app, "state", None)
            if state is not None:
                state.mail_helper = self
        return self

    def send_email(
        self,
        subject: str,
        recipients: Sequence[str],
        body: Optional[str] = None,
        html: Optional[str] = None,
        sender: Optional[str] = None,
        background_tasks: Any = None,
    ) -> bool:
        if self.config is None:
            raise RuntimeError("MailHelper is not initialized; call init_app() first")
        if not recipients:
            raise ValueError("At least one recipient is required")
        message_sender = sender or self.config.default_sender
        if not message_sender:
            raise ValueError("A sender is required; set MAIL_DEFAULT_SENDER or pass sender")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = message_sender
        message["To"] = ", ".join(recipients)
        message.set_content(body or "")
        if html is not None:
            message.add_alternative(html, subtype="html")

        if background_tasks is not None:
            background_tasks.add_task(self._send, message)
            return True
        return self._send(message)

    def _send(self, message: EmailMessage) -> bool:
        if self.config is None:
            raise RuntimeError("MailHelper is not initialized; call init_app() first")

        config = self.config
        smtp_class = smtplib.SMTP_SSL if config.use_ssl else smtplib.SMTP
        try:
            with smtp_class(config.server, config.port, timeout=config.timeout) as server:
                if config.use_tls and not config.use_ssl:
                    server.starttls()
                if config.username or config.password:
                    server.login(config.username or "", config.password or "")
                server.send_message(message)
            logger.info("Email sent to %s - %s", message["To"], message["Subject"])
            return True
        except (OSError, smtplib.SMTPException):
            logger.exception("Error sending email to %s", message["To"])
            return False


def _config_from_mapping(values: Mapping[str, Any]) -> MailConfig:
    return MailConfig(
        server=str(values["MAIL_SERVER"]),
        port=int(values.get("MAIL_PORT", 587)),
        username=values.get("MAIL_USERNAME") or None,
        password=values.get("MAIL_PASSWORD") or None,
        default_sender=values.get("MAIL_DEFAULT_SENDER") or None,
        use_tls=_as_bool(values.get("MAIL_USE_TLS", True)),
        use_ssl=_as_bool(values.get("MAIL_USE_SSL", False)),
        timeout=float(values.get("MAIL_TIMEOUT", 30)),
    )


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
