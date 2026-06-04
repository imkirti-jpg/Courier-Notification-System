from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.templates import Template
from app.schemas.templates import TemplateCreate, TemplateUpdate
from app.utils.template_renderer import validate_template_syntax

async def create_template(db: AsyncSession, data: TemplateCreate):
    validate_template_syntax(data.body)
    template = Template(**data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template

async def list_templates(db: AsyncSession):
    result = await db.execute(select(Template))
    return result.scalars().all()

async def update_template(db: AsyncSession, template_id, data: TemplateUpdate):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        return None
    updates = data.model_dump(exclude_unset=True)
    if "body" in updates:
        validate_template_syntax(updates["body"])
    for key, value in updates.items():
        setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template

async def delete_template(db: AsyncSession, template_id):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        return False
    await db.delete(template)
    await db.commit()
    return True