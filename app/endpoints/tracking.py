from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import decode_token
from app.core.database import get_db
from app.services import tracking_service

router = APIRouter()
security = HTTPBearer()


@router.post("/sessions")
def create_session(data: schemas.SessionCreate, db: Session = Depends(get_db)):
    return tracking_service.create_session(data, db)


@router.post("/events")
def create_event(data: schemas.VisitorEventIn, db: Session = Depends(get_db)):
    return tracking_service.create_event(data, db)


@router.get("/sessions/{project_id}")
def get_sessions(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return tracking_service.get_sessions(user_id, project_id, db)


@router.get("/events/{project_id}/{session_id}")
def get_events_by_session(
    project_id: int,
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return tracking_service.get_events_by_session(user_id, project_id, session_id, db)


@router.get("/events/{project_id}")
def get_events_by_project(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return tracking_service.get_events_by_project(user_id, project_id, db)


@router.delete("/session/{project_id}/{session_id}")
def delete_session(
    project_id: int,
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return tracking_service.delete_session(user_id, project_id, session_id, db)


@router.get("/page-views/{project_id}")
def page_views(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return tracking_service.get_page_views(user_id, project_id, db)


@router.get("/click/{project_id}")
def get_clicks(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return tracking_service.get_clicks(user_id, project_id, db)
