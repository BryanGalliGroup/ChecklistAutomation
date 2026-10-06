from datetime import datetime
import smtplib
from email.message import EmailMessage

from src.build_html import build_email_html
from src.build_plain import build_plain_body
from src.config import get_smtp_config


def send_email(
    body: str,
    email_settings: dict,
) -> None:
    if not isinstance(email_settings, dict):
        raise ValueError(
            "As configurações de e-mail devem ser um objeto."
        )

    subject = email_settings.get(
        "subject",
        "Checklist de Atividades | [DAY]",
    )

    subject = subject.replace(
        "[DAY]",
        datetime.now().strftime("%d/%m"),
    )

    from_name = email_settings.get(
        "from_name",
        "",
    ).strip()

    from_address = email_settings.get(
        "from_address",
        "",
    ).strip()

    recipients = email_settings.get(
        "to",
        [],
    )

    signature = email_settings.get(
        "signature",
        "",
    )

    image_url = email_settings.get(
        "image_url",
    )

    if not from_address:
        raise ValueError(
            "O endereço de origem do e-mail não foi configurado."
        )

    if not recipients:
        raise ValueError(
            "Nenhum destinatário de e-mail foi configurado."
        )

    if isinstance(recipients, str):
        recipients = [
            email.strip()
            for email in recipients.split(",")
            if email.strip()
        ]

    if not recipients:
        raise ValueError(
            "Nenhum destinatário de e-mail válido foi configurado."
        )

    plain_body = build_plain_body(
        body,
        signature,
    )

    html_body = build_email_html(
        body=body,
        signature=signature,
        image_url=image_url,
    )

    msg = EmailMessage()

    if from_name:
        msg["From"] = f"{from_name} <{from_address}>"
    else:
        msg["From"] = from_address

    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.set_content(plain_body)
    msg.add_alternative(
        html_body,
        subtype="html",
    )

    smtp_config = get_smtp_config()

    with smtplib.SMTP(
        smtp_config["host"],
        smtp_config["port"],
    ) as server:
        server.starttls()

        server.login(
            smtp_config["username"],
            smtp_config["password"],
        )

        server.send_message(msg)