from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.database.base import Base

# Import all models so SQLAlchemy registers every table.
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


engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def create_db_and_tables() -> None:
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
