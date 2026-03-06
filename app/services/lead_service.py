from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import schemas
from app.repositories import lead_repo, project_repo, tracking_repo, user_repo


def create_lead(user_id: int, data: schemas.LeadCreate, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project = project_repo.get_by_id_and_user(db, data.project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        lead = lead_repo.create(db, data, user, project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Lead with this email already exists")

    return {"message": "Lead created", "lead_id": lead.id}


def api_create_lead(tracking_key: str, session_id: str, lead_data: schemas.LeadCreate, db: Session) -> dict:
    project = project_repo.get_by_tracking_key(db, tracking_key)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    session = tracking_repo.get_session_by_public_id(db, session_id, tracking_key)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.lead:
        raise HTTPException(status_code=409, detail="Lead already exists for this session")

    try:
        lead = lead_repo.create(db, lead_data, project.user, project, visitor_session=session)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Duplicate lead")

    return {"message": "Lead created", "lead_id": lead.id}


def bulk_create_leads(user_id: int, project_id: int, leads_data: list[schemas.LeadCreate], db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project = project_repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lead_repo.bulk_create(db, leads_data, user, project)
    return {"message": "Leads created", "user_id": user.id}


def update_lead(user_id: int, project_id: int, lead_id: int, data: schemas.LeadUpdate, db: Session) -> dict:
    lead = lead_repo.get_by_id_user_project(db, lead_id, user_id, project_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_repo.update(db, lead, data)
    return {"message": "Lead updated", "lead_id": lead.id}


def delete_lead(user_id: int, project_id: int, lead_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lead = lead_repo.get_by_id_user_project(db, lead_id, user_id, project_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_repo.delete(db, lead)
    return {"message": "Lead deleted", "lead_id": lead_id}


def get_lead(user_id: int, project_id: int, lead_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lead = lead_repo.get_by_id_user_project(db, lead_id, user_id, project_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {"message": "Lead retrieved", "lead": lead}


def get_all_leads(user_id: int, project_id: int, db: Session) -> dict:
    leads = lead_repo.get_all_by_project_and_user(db, project_id, user_id)
    return {"message": "All leads fetched", "leads": leads}


def clean_leads(user_id: int, project_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lead_repo.delete_all_by_project_and_user(db, project_id, user_id)
    return {"message": "Leads cleaned", "user_id": user.id}


def attach_session_to_lead(user_id: int, lead_id: int, session_id: str, db: Session) -> dict:
    lead = lead_repo.get_by_id_and_user(db, lead_id, user_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    from app.repositories import tracking_repo as tr
    session = tr.get_session_by_public_id_and_project(db, session_id, lead.project_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.lead and session.lead.id != lead.id:
        raise HTTPException(status_code=409, detail="This session is already attached to another lead")

    lead_repo.attach_session(db, lead, session)
    return {"message": "Session attached to lead successfully", "lead_id": lead.id, "visitor_session_id": session.id}
