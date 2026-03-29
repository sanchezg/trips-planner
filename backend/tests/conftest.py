from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/trips_planner_test"
TEST_DATABASE_URL = os.environ.setdefault("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_URL", "http://testserver")
os.environ.setdefault("API_BASE_URL", "http://testserver")
os.environ.setdefault("SESSION_SECRET", "test-session-secret")
os.environ.setdefault("TOKEN_ENCRYPTION_SECRET", "test-token-secret")
os.environ.setdefault("SESSION_COOKIE_SECURE", "false")
os.environ.setdefault("SESSION_COOKIE_SAMESITE", "lax")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-client-secret")
os.environ.setdefault("GOOGLE_OAUTH_REDIRECT_URI", "http://testserver/api/routes/auth/google/callback")

from app.db.base import Base
from app.db.models import calendar, destination, event, expense, invitation, trip, trip_member, trip_share_code, user, user_session
from app.dependencies.db import get_db
from app.main import app
from app.repositories.session_repository import create_user_session
from app.db.models.user import User
from tests.factories.base import SQLAlchemySessionFactory
from tests.factories.event import EventFactory
from tests.factories.trip import TripFactory, TripMemberFactory, TripShareCodeFactory
from tests.factories.user import UserFactory, UserSessionFactory


FACTORY_CLASSES = (
    UserFactory,
    UserSessionFactory,
    TripFactory,
    TripMemberFactory,
    TripShareCodeFactory,
    EventFactory,
)


def _strip_schema_query(url: str) -> str:
    parts = urlsplit(url)
    filtered_query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "schema"]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(filtered_query), parts.fragment))


def _psycopg_conninfo(database_url: str) -> str:
    normalized = _strip_schema_query(database_url)
    if normalized.startswith("postgresql+psycopg://"):
        return "postgresql://" + normalized.removeprefix("postgresql+psycopg://")
    return normalized


def _admin_database_url(database_url: str) -> str:
    normalized = _psycopg_conninfo(database_url)
    parts = urlsplit(normalized)
    admin_path = "/postgres"
    return urlunsplit((parts.scheme, parts.netloc, admin_path, parts.query, parts.fragment))


def _database_name(database_url: str) -> str:
    normalized = _strip_schema_query(database_url)
    return urlsplit(normalized).path.removeprefix("/")


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return _strip_schema_query(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def managed_test_database(test_database_url: str) -> Generator[str, None, None]:
    database_name = _database_name(test_database_url)
    admin_url = _admin_database_url(test_database_url)

    with psycopg.connect(admin_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                (database_name,),
            )
            cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            cursor.execute(f'CREATE DATABASE "{database_name}"')

    try:
        yield test_database_url
    finally:
        with psycopg.connect(admin_url, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()",
                    (database_name,),
                )
                cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')


@pytest.fixture(scope="session")
def engine(managed_test_database: str):
    engine = create_engine(managed_test_database, future=True, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def reset_database(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture()
def db_session(session_factory) -> Generator[Session, None, None]:
    session = session_factory()
    SQLAlchemySessionFactory._meta.sqlalchemy_session = session
    for factory_class in FACTORY_CLASSES:
        factory_class._meta.sqlalchemy_session = session

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        SQLAlchemySessionFactory._meta.sqlalchemy_session = None
        for factory_class in FACTORY_CLASSES:
            factory_class._meta.sqlalchemy_session = None


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def authenticated_client(client: TestClient, db_session: Session):
    user = UserFactory()
    session_token = "session-token-" + user.id
    create_user_session(db_session, user=user, session_token=session_token)
    client.cookies.set("trip_session", session_token)
    return client, user
