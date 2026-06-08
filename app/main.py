from fastapi import FastAPI

from app.api import auth
from app.api.templates import router as templates_router
from app.api.notifications import router as notifications_router
from app.api.admin import router as admin_router

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.core.rate_limit import limiter

app = FastAPI(title="Courier",version="1.0.0")


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)



app.include_router(auth.router)
app.include_router(templates_router)
app.include_router(notifications_router)
app.include_router(admin_router)



