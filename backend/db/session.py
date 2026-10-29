from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from backend.config import settings
from backend.db.models import Base

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        settings.ensure_directories()
        _engine = create_engine(
            settings.db_url,
            connect_args={"check_same_thread": False},
            echo=settings.debug,
        )

        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=_get_engine(), autoflush=False, expire_on_commit=False)
    return _SessionLocal


def get_db() -> Session:
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        conn.execute(
            __import__("sqlalchemy").text(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
                USING fts5(text, content='chunks', content_rowid='rowid')
                """
            )
        )
        conn.commit()
