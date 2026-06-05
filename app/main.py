from fastapi import FastAPI

from app.api import auth
from app.api.templates import router as templates_router
from app.api.notifications import router as notifications_router


app = FastAPI(title="Courier",version="1.0.0")

app.include_router(auth.router)
app.include_router(templates_router)
app.include_router(notifications_router)