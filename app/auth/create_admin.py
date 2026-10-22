from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.exc import IntegrityError

from app.auth.security import hash_password
from app.database.database import SessionLocal, create_db_and_tables
from app.models.user import User


def main() -> None:
    create_db_and_tables()
    try:
        email = str(
            TypeAdapter(EmailStr).validate_python(input("Administrator email: ").strip())
        ).lower()
    except ValidationError as exc:
        raise SystemExit("Enter a valid administrator email address.") from exc
    password = getpass("Administrator password (at least 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters.")

    db = SessionLocal()
    try:
        if db.query(User.id).filter(User.email == email).first():
            raise SystemExit("An account with that email already exists.")
        db.add(
            User(
                email=email,
                password_hash=hash_password(password),
                role="ADMIN",
            )
        )
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise SystemExit("Could not create the administrator account.") from exc
    finally:
        db.close()
    print("Administrator account created.")


if __name__ == "__main__":
    main()
