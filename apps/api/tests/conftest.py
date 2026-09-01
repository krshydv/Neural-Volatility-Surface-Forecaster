import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.db.session import Base, get_db
from app.main import app

_base_url = get_settings().database_url
_root, _, _dbname = _base_url.rpartition("/")
TEST_DATABASE_URL = f"{_root}/{_dbname}_test"


@pytest.fixture(scope="session", autouse=True)
def _create_test_database():
    default_engine = create_engine(f"{_root}/postgres", isolation_level="AUTOCOMMIT")
    with default_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {_dbname}_test"))
        conn.execute(text(f"CREATE DATABASE {_dbname}_test"))
    default_engine.dispose()

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    engine.dispose()
    yield


@pytest.fixture()
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
