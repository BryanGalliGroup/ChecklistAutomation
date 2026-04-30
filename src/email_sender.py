import mimetypes
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from src.build_html import build_email_html
from src.build_plain import build_plain_body

def send_email(body: str) -> None:
    msg = EmailMessage()

    subject = os.getenv(
        "EMAIL_SUBJECT",
        "Checklist de Atividades | [DAY]"
    ).replace("[DAY]", datetime.now().strftime("%d/%m"))

    signature = os.getenv("EMAIL_SIGNATURE", "")
    image_url = os.getenv("EMAIL_IMAGE_URL")

    plain_body = build_plain_body(body, signature)
    html_body = build_email_html(
        body=body,
        signature=signature,
        image_url=image_url,
    )

    msg["From"] = os.getenv("EMAIL_FROM")
    msg["To"] = os.getenv("EMAIL_TO")
    msg["Subject"] = subject

    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)