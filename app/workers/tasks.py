from celery.exceptions import MaxRetriesExceededError
from app.workers.celery_app import celery_app
from app.db.sync_session import SyncSessionLocal
from app.models.notifications import Notification
from app.models.templates import Template
from app.models.enums import NotificationStatus
from app.utils.template_renderer import render_template
from app.services.email_service import send_email
from app.core.logging import get_logger
import uuid

logger = get_logger(__name__)

RETRY_DELAYS = [60, 120, 300, 900, 1800]   # seconds: 1m, 2m, 5m, 15m, 30m


@celery_app.task(bind=True, max_retries=5, name="send_notification")
def send_notification(self, notification_id: str):
    db = SyncSessionLocal()
    notification = None

    try:
        #  Load notification 
        notification = db.query(Notification).filter(
            Notification.id == uuid.UUID(notification_id)
        ).first()

        if not notification:
            raise ValueError(f"Notification {notification_id} not found")

        #  Mark as processing
        notification.status = NotificationStatus.PROCESSING
        db.commit()

        #  Load template
        template = db.query(Template).filter(
            Template.id == notification.template_id
        ).first()

        if not template:
            raise ValueError(f"Template {notification.template_id} not found")

        # 4. Render and send 
        rendered_subject = render_template(template.subject, notification.payload)
        rendered_body = render_template(template.body, notification.payload)

        send_email(
            to=notification.recipient,
            subject=rendered_subject,
            html_body=rendered_body
        )

        # 5. Mark as sent 
        notification.status = NotificationStatus.SENT
        db.commit()

        logger.info(
            f"notification_sent | id={notification_id} "
            f"recipient={notification.recipient}"
        )
        from celery.exceptions import Ignore


        if not notification:
            logger.error(f"notification_not_found | id={notification_id}")
            raise Ignore()    

    except Exception as exc:
        db.rollback()
        current_attempt = self.request.retries   # 0 on first failure

        if current_attempt < self.max_retries:
            _handle_retry(self, db, notification, notification_id, exc, current_attempt)
        else:
            _handle_final_failure(db, notification, notification_id, exc)

    finally:
        db.close()


def _handle_retry(task, db, notification, notification_id, exc, attempt):
    countdown = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]

    # Update status to RETRYING
    if notification:
        try:
            notification.status = NotificationStatus.RETRYING
            db.commit()
        except Exception:
            db.rollback()

    logger.warning(
        f"retry_triggered | id={notification_id} "
        f"attempt={attempt + 1}/{task.max_retries} "
        f"delay={countdown}s "
        f"error={exc}"
    )

    raise task.retry(exc=exc, countdown=countdown)


def _handle_final_failure(db, notification, notification_id, exc):
    if notification:
        try:
            notification.status = NotificationStatus.FAILED
            db.commit()
        except Exception:
            db.rollback()

    logger.error(
        f"final_failure | id={notification_id} "
        f"attempts=6 "            # 1 initial + 5 retries
        f"error={exc}"
    )

    # Phase 8 wires this up:
    # dead_letter_service.create(db, notification, exc)