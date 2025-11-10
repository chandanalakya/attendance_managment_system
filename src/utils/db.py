# src/utils/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def get_db():
    """
    Provides a transactional scope around a series of operations.
    Usage:
        with get_db() as db:
            # do stuff
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
