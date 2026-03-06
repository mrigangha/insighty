from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import decode_token
from app.core.database import get_db
from app.services import project_service

router = APIRouter()
security = HTTPBearer()


@router.post("/project")
def create_project(
    data: schemas.ProjectCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return project_service.create_project(user_id, data, db)


@router.delete("/project/{project_id}")
def delete_project(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return project_service.delete_project(user_id, project_id, db)


@router.get("/project/{project_id}")
def get_project(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return project_service.get_project(user_id, project_id, db)


@router.get("/projects")
def get_all_projects(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return project_service.get_all_projects(user_id, db)
