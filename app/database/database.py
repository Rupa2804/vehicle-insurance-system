from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.database.base import Base

# Import all model modules so SQLAlchemy registers every table.
from app.models.accident import Accident
from app.models.claim import Claim
from app.models.customer import Customer
from app.models.damage_assessment import DamageAssessment
from app.models.inspection import Inspection
from app.models.payment import Payment
from app.models.policy import Policy
from app.models.repair_estimate import RepairEstimate
from app.models.settlement import Settlement
from app.models.surveyor import Surveyor
from app.models.vehicle import Vehicle
from app.models.user import User


SQLITE_DB_URL = "sqlite:///./vehicle_insurance.db"


def _build_engine(database_url: str):
    return create_engine(database_url, pool_pre_ping=True)


def _database_is_reachable(engine: Engine) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def _use_sqlite_fallback() -> None:
    global engine, SessionLocal
    engine = _build_engine(SQLITE_DB_URL)
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )


engine = _build_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

if not _database_is_reachable(engine):
    _use_sqlite_fallback()


def create_db_and_tables() -> None:
    try:
        if not _database_is_reachable(engine):
            _use_sqlite_fallback()
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError:
        _use_sqlite_fallback()
        Base.metadata.create_all(bind=engine)


def init_db() -> None:
    create_db_and_tables()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("Database in use:", engine.dialect.name)
