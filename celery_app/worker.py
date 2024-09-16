import asyncio
from celery import Celery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
import smtplib
from smtplib import SMTPAuthenticationError

SENDER_EMAIL = config("SENDER_EMAIL")
SENDER_PASSWORD = config("SENDER_PASSWORD")

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(name="send_status_change_email")
def send_status_change_email(task_id: int, task_title: str, task_status: str, assignee_email: str):
    asyncio.run(_send_email(task_id, task_title, task_status, assignee_email))


async def _send_email(task_id: int, task_title: str, task_status: str, assignee_email: str):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
    except SMTPAuthenticationError:
        raise ValueError("Invalid email credentials. Please check your email and password.")
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = assignee_email
    msg["Subject"] = f"Status of Task №{task_id} has been changed"

    body = f'The status of Task "{task_title}" has been changed to: {task_status}'
    msg.attach(MIMEText(body, "plain"))

    server.sendmail(SENDER_EMAIL, assignee_email, msg.as_string())
    server.quit()
