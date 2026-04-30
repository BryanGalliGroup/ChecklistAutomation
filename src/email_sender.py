import mimetypes
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from html import escape
from pathlib import Path


def build_plain_body(body: str, signature: str) -> str:
    return f"""
{body}

============================================================================================
                                                                    Automação de Checklist
============================================================================================

Este é o resumo das atividades realizadas hoje, gerado automaticamente a partir das alterações realizadas no projeto.

O objetivo é fornecer uma visão clara e concisa das mudanças, melhorias e correções implementadas, facilitando o 
acompanhamento do progresso e o entendimento dos impactos positivos das alterações realizadas.

============================================================================================

{signature}
""".strip()


def build_email_html(body: str, signature: str, image_url: str | None) -> str:
    image_html = ""

    if image_url:
        image_html = f"""
        <div style="text-align: flex-start; margin: 24px 0;">
            <img 
                src="{escape(image_url)}" 
                alt="Imagem do checklist" 
                style="max-width: 600px; width: 45%; height: auto;"
            />
        </div>
        """

    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #222; line-height: 1.6;">
            <div style="white-space: pre-line;">
                {escape(body)}
            </div>

            <hr style="margin: 32px 0;" />

            <h3 style="text-align: center;">
                Automação de Checklist
            </h3>

            <p>
                Este é o resumo das atividades realizadas hoje, gerado automaticamente a partir das alterações realizadas no projeto.
            </p>

            <p>
                O objetivo é fornecer uma visão clara e concisa das mudanças, melhorias e correções implementadas,
                facilitando o acompanhamento do progresso e o entendimento dos impactos positivos das alterações realizadas.
            </p>

            <hr style="margin: 32px 0;" />

            {image_html}

            <div style="white-space: pre-line; color: #8c8c8c; font-size: 0.9em;">
                {escape(signature)}
            </div>
        </body>
    </html>
    """.strip()


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