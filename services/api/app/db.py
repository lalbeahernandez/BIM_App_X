from contextlib import contextmanager

from sqlalchemy import create_engine

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)


@contextmanager
def connection():
    with engine.begin() as conn:
        yield conn
