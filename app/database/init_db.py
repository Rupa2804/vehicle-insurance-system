
from app.database.base import Base
from app.database.database import engine

# Import models so SQLAlchemy registers their tables.
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.policy import Policy

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
