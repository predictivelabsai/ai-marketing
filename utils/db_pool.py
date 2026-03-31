"""Database connection pool for POLLY — reads DB_URL from environment."""
import os
import logging
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()
logger = logging.getLogger(__name__)


class DatabasePool:
    """SQLAlchemy connection pool with session context manager."""

    _instance = None

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DB_URL")
        if not self.database_url:
            raise ValueError("DB_URL not set.")
        self.engine = create_engine(
            self.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
        self._session_factory = sessionmaker(bind=self.engine)
        logger.info("Database pool initialized")

    @classmethod
    def get(cls, database_url: str = None) -> "DatabasePool":
        if cls._instance is None:
            cls._instance = cls(database_url)
        return cls._instance

    @contextmanager
    def get_session(self) -> Session:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
