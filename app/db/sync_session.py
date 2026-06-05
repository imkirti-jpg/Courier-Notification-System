from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.configure import settings

sync_engine = create_engine(settings.CELERY_DATABASE_URL)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()