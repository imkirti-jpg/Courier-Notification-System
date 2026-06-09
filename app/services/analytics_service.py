from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, cast, Date
from datetime import date
from app.models.notifications import Notification
from app.models.templates import Template
from app.models.enums import NotificationStatus


async def compute_analytics(
    db: AsyncSession,
    from_date: date | None = None,
    to_date: date | None = None
) -> dict:

    #  Base filter apply date range if provided 
    def apply_filters(query):
        if from_date:
            query = query.where(Notification.created_at >= from_date)
        if to_date:
            query = query.where(Notification.created_at <= to_date)
        return query


    #  Total sent 
    sent_q = apply_filters(
        select(func.count()).where(Notification.status == NotificationStatus.SENT)
    )
    total_sent = (await db.execute(sent_q)).scalar() or 0


    #  Total failed 
    failed_q = apply_filters(
        select(func.count()).where(Notification.status == NotificationStatus.FAILED)
    )
    total_failed = (await db.execute(failed_q)).scalar() or 0


    #Delivery rate 
    denominator = total_sent + total_failed
    delivery_rate = round((total_sent / denominator) * 100, 2) if denominator > 0 else 0.0


    # Retry rate 
    total_q = apply_filters(select(func.count()).select_from(Notification))
    total_all = (await db.execute(total_q)).scalar() or 0

    retried_q = apply_filters(
        select(func.count()).where(Notification.retry_count > 0)
    )
    total_retried = (await db.execute(retried_q)).scalar() or 0

    retry_rate = round((total_retried / total_all) * 100, 2) if total_all > 0 else 0.0


    #Daily breakdown — last 30 days 
    day_col = cast(Notification.created_at, Date).label("date")

    daily_q = apply_filters(
        select(
            day_col,
            func.sum(
                case((Notification.status == NotificationStatus.SENT, 1), else_=0)
            ).label("sent"),
            func.sum(
                case((Notification.status == NotificationStatus.FAILED, 1), else_=0)
            ).label("failed"),
            func.count(Notification.id).label("total")
        )
        .group_by(day_col)
        .order_by(day_col.desc())
        .limit(30)
    )

    daily_rows = (await db.execute(daily_q)).all()
    daily_breakdown = [
        {"date": row.date, "sent": row.sent, "failed": row.failed, "total": row.total}
        for row in daily_rows
    ]


    # Top 5 templates by usage 
    top_q = apply_filters(
        select(
            Template.name.label("template_name"),
            func.count(Notification.id).label("count")
        )
        .join(Template, Notification.template_id == Template.id)
        .group_by(Template.id, Template.name)
        .order_by(func.count(Notification.id).desc())
        .limit(5)
    )

    top_rows = (await db.execute(top_q)).all()
    top_templates = [
        {"template_name": row.template_name, "count": row.count}
        for row in top_rows
    ]


    return {
        "total_sent": total_sent,
        "total_failed": total_failed,
        "delivery_rate": delivery_rate,
        "retry_rate": retry_rate,
        "daily_breakdown": daily_breakdown,
        "top_templates": top_templates
    }