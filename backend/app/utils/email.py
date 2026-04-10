"""
Email notification utility (SMTP-ready placeholder).

Configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD in .env to enable.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email notification. Returns True on success, False if SMTP is not configured."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"[EMAIL STUB] To: {to_email} | Subject: {subject}")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] {exc}")
        return False


def send_booking_confirmation(to_email: str, booking_id: int, service_title: str, date: str, slot: str):
    send_email(
        to_email,
        f"UrbanCare – Booking #{booking_id} Confirmed",
        f"<h2>Booking Confirmed!</h2>"
        f"<p>Your booking for <b>{service_title}</b> on <b>{date}</b> at <b>{slot}</b> has been confirmed.</p>"
        f"<p>Thank you for choosing UrbanCare!</p>",
    )


def send_booking_reminder(to_email: str, booking_id: int, service_title: str, date: str, slot: str):
    send_email(
        to_email,
        f"UrbanCare – Reminder: Booking #{booking_id}",
        f"<h2>Upcoming Booking Reminder</h2>"
        f"<p>You have a booking for <b>{service_title}</b> on <b>{date}</b> at <b>{slot}</b>.</p>"
        f"<p>Please be ready!</p>",
    )
