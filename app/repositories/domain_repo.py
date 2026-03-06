from sqlalchemy.orm import Session

from app import models


def get_by_name(db: Session, domain_name: str) -> models.Domain | None:
    return db.query(models.Domain).filter(models.Domain.domain_name == domain_name).first()


def create(db: Session, domain_name: str) -> models.Domain:
    domain = models.Domain(domain_name=domain_name, is_active=True)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


def delete(db: Session, domain: models.Domain) -> None:
    db.delete(domain)
    db.commit()
