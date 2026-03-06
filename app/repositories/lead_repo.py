from sqlalchemy.orm import Session

from app import models
from app import schemas


def get_by_id(db: Session, lead_id: int) -> models.Lead | None:
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()


def get_by_id_user_project(db: Session, lead_id: int, user_id: int, project_id: int) -> models.Lead | None:
    return (
        db.query(models.Lead)
        .filter(
            models.Lead.id == lead_id,
            models.Lead.user_id == user_id,
            models.Lead.project_id == project_id,
        )
        .first()
    )


def get_by_id_and_user(db: Session, lead_id: int, user_id: int) -> models.Lead | None:
    return (
        db.query(models.Lead)
        .filter(models.Lead.id == lead_id, models.Lead.user_id == user_id)
        .first()
    )


def get_all_by_project_and_user(db: Session, project_id: int, user_id: int) -> list[models.Lead]:
    return (
        db.query(models.Lead)
        .filter(models.Lead.project_id == project_id, models.Lead.user_id == user_id)
        .all()
    )


def create(db: Session, data: schemas.LeadCreate, user: models.User, project: models.Project, visitor_session: models.VisitorSession | None = None) -> models.Lead:
    lead = models.Lead(
        name=data.name,
        email=data.email,
        phone=data.phone,
        source=data.source,
        status=data.status,
        user=user,
        project=project,
        visitor_session=visitor_session,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def bulk_create(db: Session, leads_data: list[schemas.LeadCreate], user: models.User, project: models.Project) -> None:
    for data in leads_data:
        lead = models.Lead(
            name=data.name,
            email=data.email,
            phone=data.phone,
            source=data.source,
            status=data.status,
            user=user,
            project=project,
        )
        db.add(lead)
    db.commit()


def update(db: Session, lead: models.Lead, data: schemas.LeadUpdate) -> models.Lead:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead


def delete(db: Session, lead: models.Lead) -> None:
    db.delete(lead)
    db.commit()


def delete_all_by_project_and_user(db: Session, project_id: int, user_id: int) -> None:
    leads = (
        db.query(models.Lead)
        .filter(models.Lead.user_id == user_id, models.Lead.project_id == project_id)
        .all()
    )
    for lead in leads:
        db.delete(lead)
    db.commit()


def attach_session(db: Session, lead: models.Lead, session: models.VisitorSession) -> models.Lead:
    lead.visitor_session = session
    db.commit()
    db.refresh(lead)
    return lead
