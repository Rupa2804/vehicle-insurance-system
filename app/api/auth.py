from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.permissions import authorize_request, require_admin
from app.auth.security import create_access_token, hash_password, verify_password
from app.database.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.models.surveyor import Surveyor
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.email == str(data.email).lower()).first()
    if user is None or not user.is_active or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=create_access_token(user.id, user.role),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(authorize_request)) -> User:
    return user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _admin: User = Depends(require_admin()),
    db: Session = Depends(get_db),
) -> list[User]:
    return db.query(User).order_by(User.id).all()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    _admin: User = Depends(require_admin()),
    db: Session = Depends(get_db),
) -> User:
    if db.query(User.id).filter(User.email == str(data.email).lower()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    if data.customer_id is not None and db.get(Customer, data.customer_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    if data.surveyor_id is not None and db.get(Surveyor, data.surveyor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Surveyor not found",
        )

    user = User(
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
        role=data.role.value,
        customer_id=data.customer_id,
        surveyor_id=data.surveyor_id,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account email, customer link, or surveyor link already exists",
        ) from exc
    db.refresh(user)
    return user
