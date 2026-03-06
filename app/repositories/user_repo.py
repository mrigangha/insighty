from sqlalchemy.orm import Session

from app import models
from app.core.auth import hash_password


def get_by_id(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def create(db: Session, name: str, email: str, password: str, pricing: str = "Free") -> models.User:
    user = models.User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        pricing_tier=pricing,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: models.User, name: str | None = None, password: str | None = None) -> models.User:
    if name:
        user.name = name
    if password:
        user.hashed_password = hash_password(password)
    db.commit()
    db.refresh(user)
    return user


def set_payment_captured(db: Session, user: models.User, payment_id: str, order_id: str) -> models.User:
    user.is_verified = True
    user.payment_id = payment_id
    user.order_id = order_id
    db.commit()
    db.refresh(user)
    return user


def set_payment_failed(db: Session, user: models.User) -> models.User:
    user.is_verified = False
    user.payment_id = None
    user.order_id = None
    db.commit()
    db.refresh(user)
    return user


def set_payment_status(db: Session, user: models.User, status: str) -> models.User:
    user.payment_status = status
    db.commit()
    db.refresh(user)
    return user


def set_order(db: Session, user: models.User, plan: str, order_id: str) -> models.User:
    user.plan = plan
    user.order_id = order_id
    user.payment_id = order_id
    db.commit()
    db.refresh(user)
    return user
