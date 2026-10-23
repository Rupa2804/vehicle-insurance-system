from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.exc import IntegrityError

from app.auth.security import hash_password
from app.database.database import SessionLocal, create_db_and_tables
from app.models.user import User
from app.schemas.common import Password


def main() -> None:
    create_db_and_tables()
    try:
        email = str(
            TypeAdapter(EmailStr).validate_python(input("Administrator email: ").strip())
        ).lower()
    except ValidationError as exc:
        raise SystemExit("Enter a valid administrator email address.") from exc
    password = getpass(
        "Administrator password (12+ characters, letters and numbers): "
    )
    try:
        TypeAdapter(Password).validate_python(password)
    except ValidationError as exc:
        raise SystemExit(
            "Password must be 12–128 characters and contain at least one "
            "letter and one number."
        ) from exc

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
