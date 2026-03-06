from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app import schemas


def get_session_by_id(db: Session, session_id: int) -> models.VisitorSession | None:
    return db.query(models.VisitorSession).filter(models.VisitorSession.id == session_id).first()


def get_session_by_public_id(db: Session, session_id: str, tracking_key: str) -> models.VisitorSession | None:
    return (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.session_id == session_id,
            models.VisitorSession.tracking_key == tracking_key,
        )
        .first()
    )


def get_session_by_public_id_and_project(db: Session, session_id: str, project_id: int) -> models.VisitorSession | None:
    return (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.session_id == session_id,
            models.VisitorSession.project_id == project_id,
        )
        .first()
    )


def get_session_by_int_id_and_project(db: Session, session_id: int, project_id: int) -> models.VisitorSession | None:
    return (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.id == session_id,
            models.VisitorSession.project_id == project_id,
        )
        .first()
    )


def get_all_sessions_by_project(db: Session, project_id: int) -> list[models.VisitorSession]:
    return db.query(models.VisitorSession).filter(models.VisitorSession.project_id == project_id).all()


def create_session(db: Session, data: schemas.SessionCreate, project_id: int) -> models.VisitorSession:
    session = models.VisitorSession(
        project_id=project_id,
        session_id=data.session_id,
        tracking_key=data.tracking_key,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session: models.VisitorSession) -> None:
    db.delete(session)
    db.commit()


def create_event(db: Session, data: schemas.VisitorEventIn, visitor_session: models.VisitorSession) -> models.VisitorEvent:
    event = models.VisitorEvent(
        project_id=visitor_session.project_id,
        visitor_session=visitor_session,
        event_type=data.event_type,
        path=data.path,
        value=data.value,
        click_target=data.click_target if data.event_type == "click" else None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_events_by_session(db: Session, session: models.VisitorSession) -> list[models.VisitorEvent]:
    return session.visitor_events


def get_events_by_project(db: Session, project_id: int) -> list[models.VisitorEvent]:
    return db.query(models.VisitorEvent).filter(models.VisitorEvent.project_id == project_id).all()


def delete_events_by_session_and_project(db: Session, session_id: int, project_id: int) -> None:
    events = (
        db.query(models.VisitorEvent)
        .filter(
            models.VisitorEvent.visitor_session_id == session_id,
            models.VisitorEvent.project_id == project_id,
        )
        .all()
    )
    for event in events:
        db.delete(event)
    db.commit()


def get_page_views_by_project(db: Session, project_id: int):
    return (
        db.query(models.VisitorEvent.path, func.count(models.VisitorEvent.id).label("count"))
        .filter(
            models.VisitorEvent.project_id == project_id,
            models.VisitorEvent.event_type == "page_view",
        )
        .group_by(models.VisitorEvent.path)
        .order_by(func.count(models.VisitorEvent.id).desc())
        .all()
    )


def get_clicks_by_project(db: Session, project_id: int):
    return (
        db.query(
            models.VisitorEvent.click_target,
            models.VisitorEvent.path,
            func.count(models.VisitorEvent.id).label("count"),
        )
        .filter(
            models.VisitorEvent.project_id == project_id,
            models.VisitorEvent.event_type == "click",
            models.VisitorEvent.click_target != "",
        )
        .group_by(models.VisitorEvent.click_target, models.VisitorEvent.path)
        .order_by(func.count(models.VisitorEvent.id).desc())
        .all()
    )
