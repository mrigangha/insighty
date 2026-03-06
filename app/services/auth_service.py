from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import create_access_token, create_refresh_token, verify_password
from app.repositories import user_repo


def register_user(data: schemas.UserCreate, db: Session) -> dict:
    if user_repo.get_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    pricing = data.pricing if data.pricing in ("Free", "Basic", "Premium") else "Free"
    user_repo.create(db, name=data.name, email=data.email, password=data.password, pricing=pricing)
    return {"message": "User created"}


def login_user(data: schemas.UserLogin, db: Session) -> JSONResponse:
    user = user_repo.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    response = JSONResponse(
        content={
            "message": "Login successful",
            "access_token": token,
            "token_type": "Bearer",
        }
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60,
        path="/",
    )
    return response


def refresh_token(user_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    token = create_access_token({"sub": str(user.id)})
    return {"message": "Refresh successful", "access_token": token, "token_type": "Bearer"}
