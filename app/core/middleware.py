from fastapi import Cookie, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session

from app.core.auth import decode_token
from app.core.database import SessionLocal
from app import models

ADMIN_ORIGINS = [
    "http://localhost:5173",
]

ADMIN_ENDPOINTS = [
    "/register", "/login", "/logout", "/refresh", "/me", "/profile",
    "/project", "/projects", "/lead", "/leads", "/clean", "/page-views", "/click", "/session",
]
TRACKING_ENDPOINTS = ["/sessions", "/events", "/api/leads"]


def is_admin_endpoint(path: str) -> bool:
    return any(path.startswith(ep) for ep in ADMIN_ENDPOINTS)


def is_tracking_endpoint(path: str) -> bool:
    return any(path.startswith(ep) for ep in TRACKING_ENDPOINTS)


def is_domain_allowed(origin: str, db: Session) -> bool:
    if not origin:
        return False
    domain = (
        db.query(models.Domain)
        .filter(models.Domain.domain_name == origin, models.Domain.is_active == True)
        .first()
    )
    return domain is not None


async def smart_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    path = request.url.path

    is_admin = origin == ADMIN_ORIGINS[0]
    is_tracking = not is_admin

    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }

        if is_admin:
            if origin in ADMIN_ORIGINS:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Access-Control-Allow-Credentials"] = "true"
                return JSONResponse(content={}, headers=headers)
            return JSONResponse(content={"detail": "Origin not allowed"}, status_code=403)

        elif is_tracking:
            if origin:
                db = SessionLocal()
                try:
                    allowed = is_domain_allowed(origin, db)
                finally:
                    db.close()
                if allowed:
                    headers["Access-Control-Allow-Origin"] = origin
                    return JSONResponse(content={}, headers=headers)
            return JSONResponse(content={"detail": "Domain not registered"}, status_code=403)

        else:
            if origin in ADMIN_ORIGINS:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Access-Control-Allow-Credentials"] = "true"
                return JSONResponse(content={}, headers=headers)

    response = await call_next(request)

    if is_admin:
        if origin in ADMIN_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
    elif is_tracking:
        if origin:
            db = SessionLocal()
            try:
                allowed = is_domain_allowed(origin, db)
                if allowed:
                    response.headers["Access-Control-Allow-Origin"] = origin
            finally:
                db.close()
    else:
        if origin in ADMIN_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


def get_current_user(refresh_token: str | None = Cookie(None)) -> int:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(refresh_token)
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
