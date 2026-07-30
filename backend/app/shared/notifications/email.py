import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import logging
from typing import Optional

from backend.app.core.config import settings

logger = logging.getLogger("agentfleet.shared.notifications.email")

def send_email_async(to_email: str, subject: str, html_content: str, text_content: str = "") -> None:
    """
    Spawns a background thread to send an email asynchronously.
    """
    thread = threading.Thread(
        target=send_email_sync,
        args=(to_email, subject, html_content, text_content)
    )
    thread.daemon = True
    thread.start()

def send_email_sync(to_email: str, subject: str, html_content: str, text_content: str = "") -> None:
    """
    Synchronously sends an email using SMTP configurations.
    Logs email details if SMTP is not configured.
    """
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASSWORD
    from_email = settings.SMTP_FROM_EMAIL

    logger.info(f"Preparing email to: {to_email} | Subject: {subject}")

    if not smtp_user or not smtp_pass:
        logger.info(
            f"SMTP credentials not fully configured (SMTP_USER/SMTP_PASSWORD). "
            f"Email simulated successfully.\n"
            f"==================================================\n"
            f"--- SIMULATED EMAIL ---\n"
            f"To: {to_email}\n"
            f"Subject: {subject}\n"
            f"Body:\n{text_content or html_content}\n"
            f"=================================================="
        )
        return

    # Build email headers and body
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    if text_content:
        msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30.0)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=30.0)
            server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        logger.info(f"Email successfully sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email} via SMTP: {e}")
