from fastapi import APIRouter, Cookie, Depends
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import decode_token
from app.core.database import get_db
from app.core.middleware import get_current_user
from app.services import auth_service

router = APIRouter()
security = HTTPBearer()


@router.post("/register")
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(data, db)


@router.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(data, db)


@router.get("/refresh")
def refresh(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return auth_service.refresh_token(user_id, db)


@router.post("/logout")
def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    from app.repositories import user_repo
    user = user_repo.get_by_id(db, payload["sub"])
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="none", path="/")
    return {"message": "Logged out"}


@router.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    return {"user_id": payload["sub"]}
