from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import decode_token
from app.core.database import get_db
from app.services import lead_service

router = APIRouter()
security = HTTPBearer()


@router.post("/lead")
def create_lead(
    data: schemas.LeadCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.create_lead(user_id, data, db)


@router.post("/api/leads/{tracking_key}/{session_id}")
def api_create_lead(
    tracking_key: str,
    session_id: str,
    lead_data: schemas.LeadCreate,
    db: Session = Depends(get_db),
):
    return lead_service.api_create_lead(tracking_key, session_id, lead_data, db)


@router.post("/leads/{project_id}/bulk")
def bulk_create_leads(
    project_id: int,
    leads_data: list[schemas.LeadCreate],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.bulk_create_leads(user_id, project_id, leads_data, db)


@router.patch("/leads/{project_id}/{lead_id}")
def update_lead(
    project_id: int,
    lead_id: int,
    data: schemas.LeadUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.update_lead(user_id, project_id, lead_id, data, db)


@router.delete("/leads/{project_id}/{lead_id}")
def delete_lead(
    project_id: int,
    lead_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.delete_lead(user_id, project_id, lead_id, db)


@router.get("/leads/{project_id}/{lead_id}")
def get_lead(
    project_id: int,
    lead_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.get_lead(user_id, project_id, lead_id, db)


@router.get("/leads/{project_id}/leads")
def get_all_leads(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.get_all_leads(user_id, project_id, db)


@router.post("/clean/{project_id}")
def clean_leads(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return lead_service.clean_leads(user_id, project_id, db)


@router.patch("/leads/{lead_id}/attach-session/{session_id}")
def attach_session_to_lead(
    lead_id: int,
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])
    return lead_service.attach_session_to_lead(user_id, lead_id, session_id, db)
