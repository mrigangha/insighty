from sqlalchemy.orm import Session

from app import models
from app.core.auth import generate_tracking_key


def get_by_id(db: Session, project_id: int) -> models.Project | None:
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_by_id_and_user(db: Session, project_id: int, user_id: int) -> models.Project | None:
    return (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.user_id == user_id)
        .first()
    )


def get_by_tracking_key(db: Session, tracking_key: str) -> models.Project | None:
    return db.query(models.Project).filter(models.Project.tracking_key == tracking_key).first()


def get_all_by_user(db: Session, user_id: int) -> list[models.Project]:
    return db.query(models.Project).filter(models.Project.user_id == user_id).all()


def count_by_user(db: Session, user_id: int) -> int:
    return db.query(models.Project).filter(models.Project.user_id == user_id).count()


def create(db: Session, name: str, domain: str, user: models.User) -> models.Project:
    project = models.Project(
        name=name,
        domain=domain,
        user=user,
        tracking_key=generate_tracking_key(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project: models.Project) -> None:
    db.delete(project)
    db.commit()
