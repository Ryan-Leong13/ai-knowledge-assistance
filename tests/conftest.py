"""
Shared pytest fixtures

Test run against an isolated in-memory SQLite database, via FastAPI's 
dependency override mechanism. This means that the test suite never 
depends or pollute whatever is currently seeded locally
"""
import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.services import document_func


# A fresh, temporary file-backed database, created and deleted per test.
@pytest.fixture()
def db_session():

    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
    Base.metadata.create_all(bind = engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()
        os.close(db_fd)
        os.remove(db_path)


# A TestClient wired to use the isolated test DB
@pytest.fixture()
def client(db_session):

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# A client whose test database already has a small, known set of documents 
# used by chat/retrieval tests that need real content to retrieve against.
@pytest.fixture()
def seeded_client(client, db_session):

    document_func.create_doc(
        db_session,
        title = "Password Reset",
        content = (
            "Employees can reset their own password via the Identity Portal "
            "at https://identity.blacksmithdata.internal/reset. Passwords "
            "expire every 90 days."
        ),
    )

    document_func.create_doc(
        db_session,
        title = "Leave Application",
        content = (
            "Full-time employees accrue annual leave starting at 14 days "
            "per year. Sick leave requires a Medical Certificate. "
            "Compassionate leave is up to 3 days for bereavement."
        ),
    )

    document_func.create_doc(
        db_session,
        title = "Office WiFi",
        content = (
            "Connect to the Blacksmith-Staff network using your company "
            "email and password. Guest WiFi password changes weekly."
        ),
    )
    return client