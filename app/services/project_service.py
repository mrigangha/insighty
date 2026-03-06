from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.repositories import domain_repo, lead_repo, project_repo, user_repo


def create_project(user_id: int, data: schemas.ProjectCreate, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    count = project_repo.count_by_user(db, user_id)
    if user.pricing_tier == "Free" and count >= 3:
        raise HTTPException(status_code=403, detail="Max projects reached")
    elif user.pricing_tier == "Basic" and count >= 10:
        raise HTTPException(status_code=403, detail="Max projects reached")

    project = project_repo.create(db, name=data.name, domain=data.domain, user=user)

    if not domain_repo.get_by_name(db, data.domain):
        domain_repo.create(db, data.domain)

    return {"message": "Project created", "project_id": project.id}


def delete_project(user_id: int, project_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project = project_repo.get_by_id_and_user(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    lead_repo.delete_all_by_project_and_user(db, project.id, user_id)

    domain = domain_repo.get_by_name(db, project.domain)
    project_repo.delete(db, project)
    if domain:
        domain_repo.delete(db, domain)

    return {"message": "Project deleted", "project_id": project_id}


def get_project(user_id: int, project_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project = project_repo.get_by_id_and_user(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"message": "Project fetched", "project": project}


def get_all_projects(user_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    projects = project_repo.get_all_by_user(db, user_id)
    return {"message": "Projects fetched", "projects": projects}
