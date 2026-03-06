from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.repositories import project_repo, tracking_repo


def create_session(data: schemas.SessionCreate, db: Session) -> dict:
    project = project_repo.get_by_tracking_key(db, data.tracking_key)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tracking_repo.create_session(db, data, project.id)
    return {"message": "Session created"}


def create_event(data: schemas.VisitorEventIn, db: Session) -> dict:
    project = project_repo.get_by_tracking_key(db, data.tracking_key)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    visitor_session = tracking_repo.get_session_by_public_id_and_project(db, data.session_id, project.id)
    if not visitor_session:
        raise HTTPException(status_code=404, detail="Unauthorised not found")

    event = tracking_repo.create_event(db, data, visitor_session)
    return {"message": "Event created", "event_id": event.id}


def get_sessions(user_id: int, project_id: int, db: Session) -> dict:
    project = project_repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    sessions = tracking_repo.get_all_sessions_by_project(db, project_id)
    return {"message": "Sessions retrieved", "sessions": sessions}


def get_events_by_session(user_id: int, project_id: int, session_id: int, db: Session) -> dict:
    project = project_repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    session = tracking_repo.get_session_by_int_id_and_project(db, session_id, project_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"message": "Sessions Events retrieved", "session": session.visitor_events}


def get_events_by_project(user_id: int, project_id: int, db: Session) -> dict:
    project = project_repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    events = tracking_repo.get_events_by_project(db, project_id)
    return {"message": "Events retrieved", "events": events}


def delete_session(user_id: int, project_id: int, session_id: int, db: Session) -> dict:
    session = tracking_repo.get_session_by_int_id_and_project(db, session_id, project_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    tracking_repo.delete_events_by_session_and_project(db, session_id, project_id)
    tracking_repo.delete_session(db, session)
    return {"message": "Session deleted"}


def get_page_views(user_id: int, project_id: int, db: Session) -> dict:
    project = project_repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    results = tracking_repo.get_page_views_by_project(db, project_id)
    return {"views": [{"path": path, "count": count} for path, count in results]}


def get_clicks(user_id: int, project_id: int, db: Session) -> dict:
    project = project_repo.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    results = tracking_repo.get_clicks_by_project(db, project_id)
    return {"clicks": [{"target": t, "path": p, "count": c} for t, p, c in results]}
