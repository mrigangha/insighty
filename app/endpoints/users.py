from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import decode_token
from app.core.database import get_db
from app.services import user_service

router = APIRouter()
security = HTTPBearer()


@router.get("/profile")
def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return user_service.get_profile(user_id, db)


@router.put("/profile")
def update_profile(
    data: schemas.UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return user_service.update_profile(user_id, data, db)
