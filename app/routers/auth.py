from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import timedelta

from app.schemas.user import UserLogin, Token, UserCreate, UserResponse
from app.database import get_db, Base, engine, SessionLocal
from app.models.user import User
from app.crud.user import get_user_by_email, create_user
from app.dependencies import get_current_user
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["autenticación"])

# Crear tablas DB si no existen
Base.metadata.create_all(bind=engine)

# Semilla de usuarios de ejemplo
def create_default_users():
    db = SessionLocal()
    try:
        if not get_user_by_email(db, "test@example.com"):
            create_user(
                db,
                email="test@example.com",
                name="Usuario Test",
                hashed_password=get_password_hash("123456"),
                role="user"
            )
        if not get_user_by_email(db, "admin@example.com"):
            create_user(
                db,
                email="admin@example.com",
                name="Administrador",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
    finally:
        db.close()

create_default_users()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = create_user(
        db,
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
        role="user"
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
    )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
    )
