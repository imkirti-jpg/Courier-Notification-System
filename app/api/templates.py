from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.schemas.templates import TemplateCreate, TemplateUpdate, TemplateResponse
from app.services import template as template_service

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.post("/", response_model=TemplateResponse, status_code=201)
async def create(data: TemplateCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await template_service.create_template(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[TemplateResponse])
async def list_all(db: AsyncSession = Depends(get_db)):
    return await template_service.list_templates(db)

@router.put("/{template_id}", response_model=TemplateResponse)
async def update(template_id, data: TemplateUpdate, db: AsyncSession = Depends(get_db)):
    template = await template_service.update_template(db, template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.delete("/{template_id}", status_code=204)
async def delete(template_id, db: AsyncSession = Depends(get_db)):
    deleted = await template_service.delete_template(db, template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")