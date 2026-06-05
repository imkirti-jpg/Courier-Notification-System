from app.workers.celery_app import celery_app
from app.db.sync_session import SyncSessionLocal
from app.models.notifications import Notification
from app.models.templates import Template
from app.models.auth import User
from app.models.enums import NotificationStatus
from app.utils.template_renderer import render_template
from app.services.email_service import send_email
import uuid

@celery_app.task(bind=True, name="send_notification")
def send_notification(self, notification_id: str):
    db = SyncSessionLocal()
    try:
        # 1. Load the notification
        notification = db.query(Notification).filter(
            Notification.id == uuid.UUID(notification_id)
        ).first()

        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        # 2. Mark as processing before doing any work
        notification.status = NotificationStatus.PROCESSING
        db.commit()

        # 3. Load the template
        template = db.query(Template).filter(
            Template.id == notification.template_id
        ).first()

        if not template:
            raise ValueError(f"Template {notification.template_id} not found")

        # 4. Render subject and body with the notification's payload
        rendered_subject = render_template(template.subject, notification.payload)
        rendered_body = render_template(template.body, notification.payload)

        # 5. Send the email
        send_email(
            to=notification.recipient,
            subject=rendered_subject,
            html_body=rendered_body
        )

        # 6. Mark as sent
        notification.status = NotificationStatus.SENT
        db.commit()

    except Exception as exc:
        db.rollback()

        # Mark as failed — Phase 7 will replace this with retry logic
        try:
            if notification:
                notification.status = NotificationStatus.FAILED
                db.commit()
        except Exception:
            db.rollback()

        raise exc

    finally:
        db.close()