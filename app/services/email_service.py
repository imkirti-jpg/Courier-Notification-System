import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.configure import settings
import sendgrid
from sendgrid.helpers.mail import Mail



def send_email_smtp(to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to

    # Attach as HTML — plain text fallback is optional but good practice
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        # Only authenticate if credentials are provided
        # Mailhog needs no auth; real SMTP providers do
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        print(f"Sending email to {to}")

        smtp.sendmail(settings.EMAIL_FROM, to, msg.as_string())




def send_email_sendgrid(to: str, subject: str, html_body: str) -> None:
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    message = Mail(
        from_email=settings.EMAIL_FROM,
        to_emails=to,
        subject=subject,
        html_content=html_body
    )
    sg.send(message)




def send_email(to: str, subject: str, html_body: str) -> None:
    if settings.SENDGRID_API_KEY:
        send_email_sendgrid(to, subject, html_body)
    else:
        send_email_smtp(to, subject, html_body)