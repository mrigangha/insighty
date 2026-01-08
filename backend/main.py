import hashlib
import hmac
import json
from contextlib import asynccontextmanager
from typing import Optional

import models
import razorpay
import schemas
from auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_tracking_key,
    get_domain,
    hash_password,
    verify_password,
)
from bson import ObjectId
from database import Base, SessionLocal, engine
from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import Lead, User
from pydantic.types import PastDate
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

app = FastAPI()
Base.metadata.create_all(bind=engine)
razorpay_client = razorpay.Client(
    auth=("rzp_test_RznNlAeuXL0d3K", "quzU643RrL3EC6pEbQHzOUc3")
)
"""
origins = [
    "http://localhost:5173",  # your frontend origin
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""
ADMIN_ORIGINS = [
    "http://localhost:5173",
    # Add production admin URL when ready
]

# Only two categories: ADMIN and TRACKING
ADMIN_ENDPOINTS = [
    "/register",
    "/login",
    "/logout",
    "/refresh",
    "/me",
    "/profile",
    "/project",
    "/projects",
    "/lead",
    "/leads",
    "/clean",
    "/page-views",
    "/click",
    "/session",
]
TRACKING_ENDPOINTS = ["/sessions", "/events", "/api/leads"]


def is_admin_endpoint(path: str) -> bool:
    """Check if endpoint is for admin dashboard"""
    return any(path.startswith(ep) for ep in ADMIN_ENDPOINTS)


def is_tracking_endpoint(path: str) -> bool:
    """Check if endpoint is for client tracking"""
    return any(path.startswith(ep) for ep in TRACKING_ENDPOINTS)


def is_domain_allowed(origin: str, db: Session) -> bool:
    """Check if domain is whitelisted"""
    if not origin:
        return False

    domain = (
        db.query(models.Domain)
        .filter(models.Domain.domain_name == origin, models.Domain.is_active == True)
        .first()
    )

    return domain is not None


@app.middleware("http")
async def smart_cors_middleware(request: Request, call_next):
    """
    Two-tier CORS:
    - Admin endpoints: ADMIN_ORIGINS with credentials (for dashboard)
    - Tracking endpoints: Check domains table (for client websites)
    """

    origin = request.headers.get("origin")
    path = request.url.path

    is_admin = is_admin_endpoint(path)
    is_tracking = is_tracking_endpoint(path)
    if ADMIN_ORIGINS[0] == origin:
        is_admin = True
        is_tracking = False
    else:
        is_admin = False
        is_tracking = True
    """
    print("=" * 50)
    print(f"📍 Path: {path}")
    print(f"🌐 Origin: {origin}")
    print(f"🔧 Is Admin: {is_admin}")  # ← ADD THIS
    print(f"📊 Is Tracking: {is_tracking}")  # ← ADD THIS
    print("=" * 50)
    """

    # Handle preflight (OPTIONS)
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }

        if is_admin:
            # Admin dashboard: strict whitelist with cookies
            if origin in ADMIN_ORIGINS:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Access-Control-Allow-Credentials"] = "true"
                return JSONResponse(content={}, headers=headers)
            return JSONResponse(
                content={"detail": "Origin not allowed"}, status_code=403
            )

        elif is_tracking:
            # Client websites: check database
            print(origin)
            if origin:
                db = SessionLocal()
                try:
                    allowed = is_domain_allowed(origin, db)
                finally:
                    db.close()

                if allowed:
                    headers["Access-Control-Allow-Origin"] = origin
                    return JSONResponse(content={}, headers=headers)
            return JSONResponse(
                content={"detail": "Domain not registered"}, status_code=403
            )

        else:
            # Default: admin only
            if origin in ADMIN_ORIGINS:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Access-Control-Allow-Credentials"] = "true"
                return JSONResponse(content={}, headers=headers)

    # Process request
    response = await call_next(request)

    # Add CORS headers
    if is_admin:
        # Admin dashboard
        if origin in ADMIN_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"

    elif is_tracking:
        # Client websites
        if origin:
            db = SessionLocal()
            try:
                allowed = is_domain_allowed(origin, db)
                if allowed:
                    response.headers["Access-Control-Allow-Origin"] = origin
            finally:
                db.close()

    else:
        # Default: admin
        if origin in ADMIN_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


IS_PROD = False  # True in production


def get_current_user(
    refresh_token: str | None = Cookie(None),  # Match the cookie name!
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@app.post("/register")
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(data.password)

    new_user = models.User(name=data.name, email=data.email, hashed_password=hashed)
    if data.pricing == "Free":
        new_user.pricing_tier = "Free"
    elif data.pricing == "Basic":
        new_user.pricing_tier = "Basic"
    elif data.pricing == "Premium":
        new_user.pricing_tier = "Premium"
    print(new_user.pricing_tier)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}


@app.get("/refresh")
def get_me(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    token = create_access_token({"sub": str(user.id)})
    return {
        "message": "Refresh successful",
        "access_token": token,
        "token_type": "Bearer",
    }


@app.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    print("Bad")
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    response = JSONResponse(
        content={
            "message": "Login successful",
            "access_token": token,
            "token_type": "Bearer",
        }
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # 🔐 JS cannot access
        secure=True,  # 🔒 HTTPS only (SET FALSE for local dev)
        samesite="none",
        max_age=60 * 60,
        path="/",
    )
    return response


security = HTTPBearer()


@app.post("/paymentorder")  # Changed to POST
def create_order(
    order_data: schemas.OrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        # Verify token and get user
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload["sub"]

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        # Check if free plan
        if order_data.amount == 0:
            raise HTTPException(
                status_code=400, detail="Free plan doesn't require payment"
            )

        # Create Razorpay order
        order = razorpay_client.order.create(
            {
                "amount": order_data.amount,  # Fixed typo
                "currency": order_data.currency,
                "payment_capture": 1,  # Added this
                "notes": {  # Plan goes here, not in main dict
                    "plan": order_data.plan,
                    "user_id": user_id,  # Optional: for tracking
                },
            }
        )

        # Return formatted response
        user.order_id = order["id"]
        user.payment_id = order["id"]
        db.commit()
        db.refresh(user)
        print(order["id"])
        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "status": order["status"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@app.post("/logout")
async def logout(
    response: Response,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    response.delete_cookie(
        key="refresh_token",
        httponly=True,  # 🔐 JS cannot access
        secure=True,  # 🔒 HTTPS only (SET FALSE for local dev)
        samesite="none",
        path="/",
    )
    return {"message": "Logged Up"}


@app.post("/verifypayment")
def verify_payment(
    payment: schemas.PaymentVerification,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Verify Razorpay payment signature
    This is PUBLIC endpoint - no auth required for registration flow
    """
    try:
        # Create params dict for signature verification
        params_dict = {
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": payment.razorpay_payment_id,
            "razorpay_signature": payment.razorpay_signature,
        }

        # Verify signature using Razorpay client
        # This will raise SignatureVerificationError if invalid
        razorpay_client.utility.verify_payment_signature(params_dict)

        # If we reach here, signature is valid
        # Fetch payment details from Razorpay
        payment_details = razorpay_client.payment.fetch(payment.razorpay_payment_id)

        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload["sub"]

        user = db.query(models.User).filter(models.User.id == user_id).first()
        user.is_verified = True
        user.payment_id = payment.razorpay_payment_id
        user.order_id = payment.razorpay_order_id
        db.commit()
        db.refresh(user)
        return {
            "status": "success",
            "message": "Payment verified successfully",
            "payment_details": {
                "payment_id": payment.razorpay_payment_id,
                "order_id": payment.razorpay_order_id,
                "amount": payment_details["amount"],
                "currency": payment_details["currency"],
                "status": payment_details["status"],
            },
        }

    except SignatureVerificationError:
        # Signature doesn't match - payment is fake/tampered
        raise HTTPException(
            status_code=400,
            detail="Invalid payment signature. Payment verification failed.",
        )

    except Exception as e:
        # Other errors (network, Razorpay API issues, etc.)
        print(f"Payment verification error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Payment verification failed: {str(e)}"
        )


@app.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)

    return {"user_id": payload["sub"]}


@app.get("/profile")
def profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pricing = user.pricing_tier
    if not user.is_verified:
        user.pricing_tier = "Free"
        db.commit()
        db.refresh(user)
        pricing = "Free"
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "plan": pricing,
    }


@app.put("/profile")
def update_profile(
    data: schemas.UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.name:
        user.name = data.name
    if data.password:
        user.hashed_password = hash_password(data.password)

    db.commit()
    db.refresh(user)

    return {"message": "Profile updated", "user_id": user.id}


@app.post("/project")
def create_project(
    data: schemas.ProjectCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    no_of_projects = (
        db.query(models.Project).filter(models.Project.user_id == user_id).count()
    )
    if user.pricing_tier == "Free" and no_of_projects >= 3:
        raise HTTPException(status_code=403, detail="Max projects reached")
    elif user.pricing_tier == "Basic" and no_of_projects >= 10:
        raise HTTPException(status_code=403, detail="Max projects reached")
    project = models.Project(
        name=data.name,
        domain=data.domain,
        user=user,
        tracking_key=generate_tracking_key(),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    existing_domain = (
        db.query(models.Domain).filter(models.Domain.domain_name == data.domain).first()
    )

    if not existing_domain:
        domain = models.Domain(domain_name=data.domain, is_active=1)
        db.add(domain)
        db.commit()
        db.refresh(domain)

    return {"message": "Project created", "project_id": project.id}


@app.delete("/project/{project_id}")
def delete_project(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id, models.Project.user_id == user_id)
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    leads = (
        db.query(models.Lead)
        .filter(models.Lead.project_id == project.id, models.Lead.user_id == user_id)
        .all()
    )
    for lead in leads:
        db.delete(lead)
    domain_name = project.domain
    domain = (
        db.query(models.Domain).filter(models.Domain.domain_name == domain_name).first()
    )
    db.delete(project)
    db.delete(domain)
    db.commit()

    return {"message": "Project deleted", "project_id": project_id}


@app.get("/project/{project_id}")
def get_project(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    project = (
        db.query(models.Project)
        .filter(
            models.Project.id == project_id,
            models.Project.user_id == user_id,
        )
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"message": "Project fetched", "project": project}


@app.get("/projects")
def get_projects(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    projects = db.query(models.Project).filter(models.Project.user_id == user_id).all()

    return {"message": "Projects fetched", "projects": projects}


@app.post("/lead")
def create_lead(
    data: schemas.LeadCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = (
        db.query(models.Project)
        .filter(models.Project.id == data.project_id, models.Project.user_id == user_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

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
    try:
        db.commit()
        db.refresh(lead)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Lead with this email already exists"
        )
    return {"message": "Lead created", "lead_id": lead.id}


@app.post("/leads/{project_id}/bulk")
def bulk_create_leads(
    project_id: int,
    leads_data: list[schemas.LeadCreate],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
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

    return {"message": "Leads created", "user_id": user.id}


@app.post("/clean/{project_id}")
def clean_leads(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    leads = (
        db.query(models.Lead)
        .filter(models.Lead.user_id == user_id, models.Lead.project_id == project_id)
        .all()
    )

    for lead in leads:
        db.delete(lead)

    db.commit()

    return {"message": "Leads cleaned", "user_id": user.id}


@app.get("/leads/{project_id}/leads")
def get_all_leads(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]

    leads = (
        db.query(models.Lead)
        .filter(
            models.Lead.project_id == project_id,
            models.Lead.user_id == user_id,
        )
        .all()
    )

    return {"message": "All leads fetched", "leads": leads}


@app.patch("/leads/{project_id}/{lead_id}")
def update_lead(
    project_id: int,
    lead_id: int,
    data: schemas.LeadUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]

    # Fetch lead that belongs to THIS user only
    lead = (
        db.query(models.Lead)
        .filter(
            models.Lead.id == lead_id,
            models.Lead.project_id == project_id,
            models.Lead.user_id == user_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Update only provided fields
    for field, value in data.dict(exclude_unset=True).items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)

    return {"message": "Lead updated", "lead_id": lead.id}


@app.delete("/leads/{project_id}/{lead_id}")
def delete_lead(
    project_id: int,
    lead_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lead = (
        db.query(models.Lead)
        .filter(
            models.Lead.id == lead_id,
            models.Lead.project_id == project_id,
            models.Lead.user_id == user_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()

    return {"message": "Lead deleted", "lead_id": lead_id}


@app.get("/leads/{project_id}/{lead_id}")
def get_lead(
    project_id: int,
    lead_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload["sub"]

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    lead = (
        db.query(models.Lead)
        .filter(
            models.Lead.id == lead_id,
            models.Lead.project_id == project_id,
            models.Lead.user_id == user_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {"message": "Lead retrieved", "lead": lead}


@app.post("/sessions")
def create_session(
    data: schemas.SessionCreate,
    db: Session = Depends(get_db),
):
    project = (
        db.query(models.Project)
        .filter(models.Project.tracking_key == data.tracking_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session = models.VisitorSession(
        project_id=project.id,
        session_id=data.session_id,
        tracking_key=data.tracking_key,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "message": "Session created",
    }


@app.post("/events")
def create_event(data: schemas.VisitorEventIn, db: Session = Depends(get_db)):
    project = (
        db.query(models.Project)
        .filter(models.Project.tracking_key == data.tracking_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    visitor_session = (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.session_id == data.session_id,
            models.VisitorSession.project_id == project.id,
        )
        .first()
    )

    if not visitor_session:
        raise HTTPException(status_code=404, detail="Unauthorised not found")

    if data.event_type == "click":
        event = models.VisitorEvent(
            project_id=visitor_session.project_id,
            visitor_session=visitor_session,
            event_type=data.event_type,
            path=data.path,
            value=data.value,
            click_target=data.click_target,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
    else:
        event = models.VisitorEvent(
            project_id=visitor_session.project_id,
            visitor_session=visitor_session,
            event_type=data.event_type,
            path=data.path,
            value=data.value,
        )
        db.add(event)
        db.commit()
        db.refresh(event)

    return {"message": "Event created", "event_id": event.id}


@app.get("/sessions/{project_id}")
def get_sessions(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = int(payload["sub"])
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    sessions = (
        db.query(models.VisitorSession)
        .filter(models.VisitorSession.project_id == project_id)
        .all()
    )

    return {"message": "Sessions retrieved", "sessions": sessions}


@app.get("/events/{project_id}/{session_id}")
def get_events(
    project_id: int,
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = int(payload["sub"])
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    session = (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.project_id == project_id,
            models.VisitorSession.id == session_id,
        )
        .first()
    )

    return {"message": "Sessions Events retrieved", "session": session.visitor_events}


@app.get("/events/{project_id}")
def get_event_by_project_id(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = int(payload["sub"])
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    events = (
        db.query(models.VisitorEvent)
        .filter(models.VisitorEvent.project_id == project_id)
        .all()
    )

    return {"message": "Events retrieved", "events": events}


@app.get("/page-views/{project_id}")
def page_views(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            models.VisitorEvent.path, func.count(models.VisitorEvent.id).label("count")
        )
        .filter(
            models.VisitorEvent.project_id == project_id,
            models.VisitorEvent.event_type == "page_view",
        )
        .group_by(models.VisitorEvent.path)
        .order_by(func.count(models.VisitorEvent.id).desc())
        .all()
    )

    return {"views": [{"path": path, "count": count} for path, count in results]}


@app.get("/click/{project_id}")
def get_clicks(
    project_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    results = (
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

    return {
        "clicks": [
            {"target": click_target, "path": path, "count": count}
            for click_target, path, count in results
        ]
    }


@app.delete("/session/{project_id}/{session_id}")
def delete_session(
    project_id: int,
    session_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = int(payload["sub"])
    session = (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.project_id == project_id,
            models.VisitorSession.id == session_id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    leads = (
        db.query(models.VisitorEvent)
        .filter(
            models.VisitorEvent.visitor_session_id == session_id,
            models.VisitorEvent.project_id == project_id,
        )
        .all()
    )
    for lead in leads:
        db.delete(lead)

    db.delete(session)
    db.commit()

    return {"message": "Session deleted"}


@app.post("/api/leads/{tracking_key}/{session_id}")
def api_create_lead(
    tracking_key: str,
    session_id: str,  # ✅ FIXED
    lead_data: schemas.LeadCreate,
    db: Session = Depends(get_db),
):
    # 1️⃣ Get project
    project = (
        db.query(models.Project)
        .filter(models.Project.tracking_key == tracking_key)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2️⃣ Get session (project-safe)
    session = (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.session_id == session_id,
            models.VisitorSession.tracking_key == tracking_key,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 3️⃣ Prevent duplicate session → lead
    if session.lead:
        raise HTTPException(
            status_code=409,
            detail="Lead already exists for this session",
        )

    # 4️⃣ Create lead
    lead = models.Lead(
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        source=lead_data.source,
        status=lead_data.status,
        user=project.user,
        project=project,
        visitor_session=session,
    )

    db.add(lead)
    try:
        db.commit()
        db.refresh(lead)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate lead",
        )

    return {
        "message": "Lead created",
        "lead_id": lead.id,
    }


@app.patch("/leads/{lead_id}/attach-session/{session_id}")
def attach_session_to_lead(
    lead_id: int,
    session_id: str,  # public session_id (JS)
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = int(decode_token(credentials.credentials)["sub"])

    # 1️⃣ Fetch lead (user-safe)
    lead = (
        db.query(models.Lead)
        .filter(
            models.Lead.id == lead_id,
            models.Lead.user_id == user_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # 2️⃣ Fetch session (project-safe)
    session = (
        db.query(models.VisitorSession)
        .filter(
            models.VisitorSession.session_id == session_id,
            models.VisitorSession.project_id == lead.project_id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 3️⃣ Check if session already attached to another lead
    if session.lead and session.lead.id != lead.id:
        raise HTTPException(
            status_code=409,
            detail="This session is already attached to another lead",
        )

    # 4️⃣ Attach session to lead
    lead.visitor_session = session

    db.commit()
    db.refresh(lead)

    return {
        "message": "Session attached to lead successfully",
        "lead_id": lead.id,
        "visitor_session_id": session.id,
    }


# You'll add this AFTER Blazerpay gives it to you
BLAZERPAY_WEBHOOK_SECRET = "virvir123"


def verify_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        BLAZERPAY_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


@app.post("/webhooks/blazerpay")
async def handle_webhook(
    request: Request,
    x_blazerpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    raw_body = await request.body()

    # Verify signature (add this after you get the secret)
    if BLAZERPAY_WEBHOOK_SECRET != "virvir123":
        if not x_blazerpay_signature or not verify_signature(
            raw_body, x_blazerpay_signature
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(raw_body)
    event = payload.get("event")

    if event == "payment.captured":
        email = payload.get("payload").get("payment").get("entity").get("email")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found for email: {email}")
            raise HTTPException(status_code=404, detail="User not found")
        user.is_verified = True
        user.payment_id = payload.get("payload").get("payment").get("entity").get("id")
        user.order_id = (
            payload.get("payload").get("payment").get("entity").get("order_id")
        )
        db.commit()
        db.refresh(user)

        # TODO: Your logic here

    elif event == "payment.failed":
        email = payload.get("payload").get("payment").get("entity").get("email")
        user = db.query(User).filter(User.email == email).first()
        user.is_verified = False
        user.payment_id = None
        user.order_id = None
        db.commit()
        db.refresh(user)

    return {"status": "received"}
