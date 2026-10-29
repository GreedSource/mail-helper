from email.message import EmailMessage
from unittest.mock import MagicMock, patch

import pytest

from mail_helper import MailConfig, MailHelper


def test_send_email_uses_tls_and_message_fields():
    helper = MailHelper(
        MailConfig(
            server="smtp.example.com",
            default_sender="noreply@example.com",
        )
    )
    smtp = MagicMock()
    smtp.__enter__.return_value = smtp

    with patch("mail_helper.mail.smtplib.SMTP", return_value=smtp):
        result = helper.send_email(
            "Hello",
            ["person@example.com"],
            body="Text",
            html="<p>HTML</p>",
        )

    assert result is True
    smtp.starttls.assert_called_once()
    sent = smtp.send_message.call_args.args[0]
    assert isinstance(sent, EmailMessage)
    assert sent["From"] == "noreply@example.com"
    assert sent["To"] == "person@example.com"
    assert sent.get_body(preferencelist=("plain",)).get_content().strip() == "Text"


def test_background_tasks_enqueue_send_without_connecting():
    helper = MailHelper(
        MailConfig(server="smtp.example.com", default_sender="sender@example.com")
    )
    background_tasks = MagicMock()

    assert helper.send_email(
        "Hello", ["person@example.com"], background_tasks=background_tasks
    )
    background_tasks.add_task.assert_called_once()
    assert background_tasks.add_task.call_args.args[0] == helper._send


def test_missing_sender_is_reported():
    helper = MailHelper(MailConfig(server="smtp.example.com"))

    with pytest.raises(ValueError, match="sender is required"):
        helper.send_email("Hello", ["person@example.com"])
