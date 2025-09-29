import os
import ssl
import logging
import smtplib
import json
from email.message import EmailMessage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))


def send_email(to_addr: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER or "no-reply@example.com"
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.ehlo()
        if SMTP_PORT == 587:
            server.starttls(context=context)
            server.ehlo()
        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    logger.info(f"Email enviado a: {to_addr}")


def lambda_handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        subject = body.get("subject")
        message = body.get("body")
        to_addr = body.get("to") or body.get("emailTo")

        if not subject or not message or not to_addr:
            logger.error(f"Mensaje inválido: {body}")
            continue

        try:
            send_email(to_addr, subject, message)
        except Exception as e:
            logger.exception(f"Error enviando correo a {to_addr}: {e}")

