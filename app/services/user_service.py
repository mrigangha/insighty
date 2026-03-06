from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.repositories import user_repo


def get_profile(user_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pricing = user.pricing_tier if user.is_verified else "Free"
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "plan": pricing,
        "payment_status": user.is_verified,
        "original_plan": user.pricing_tier,
    }


def update_profile(user_id: int, data: schemas.UserUpdate, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.update(db, user, name=data.name, password=data.password)
    return {"message": "Profile updated", "user_id": user.id}
