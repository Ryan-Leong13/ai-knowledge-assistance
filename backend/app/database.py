"""
Database engine and session configuration
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv(
    "Database URL", "sqlite:///./backend/app/data/knowledge_base.db"
)

# check_same_thread = False is required for SQLite when used with FastAPI's threaded request handling
engine = create_engine(
    DB_URL, connect_args = {"check_same_thread" : False}
)

# "autocommit=False" is to force the operations to call db.commit() to persist changes, 
# preventing unintended overwrites
# "autoflush=False" prevents automatic flushing of pending changes to the db before running queries, 
# giving the app explicit control
SessionLocal = sessionmaker(autocommit = False , autoflush = False , bind = engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()