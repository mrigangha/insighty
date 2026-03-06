from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    pricing_tier = Column(String(50), default="Free")
    is_verified = Column(Boolean, default=False)
    payment_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    payment_status = Column(String, nullable=True, default="not_started")

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False)
    tracking_key = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="projects")
    leads = relationship("Lead", back_populates="project")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    source = Column(String(255), nullable=True)
    status = Column(String(50), default="New")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    visitor_session_id = Column(Integer, ForeignKey("visitor_sessions.id"), nullable=True, unique=True)

    user = relationship("User", back_populates="leads")
    project = relationship("Project", back_populates="leads")
    visitor_session = relationship("VisitorSession", back_populates="lead", uselist=False)
    score = relationship("LeadScore", uselist=False, back_populates="lead", cascade="all, delete-orphan")


class VisitorSession(Base):
    __tablename__ = "visitor_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    tracking_key = Column(String(255), index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    lead = relationship("Lead", back_populates="visitor_session", uselist=False)
    visitor_events = relationship("VisitorEvent", back_populates="visitor_session", cascade="all, delete-orphan")


class VisitorEvent(Base):
    __tablename__ = "visitor_events"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)
    visitor_session_id = Column(Integer, ForeignKey("visitor_sessions.id"), index=True, nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), index=True, nullable=True)
    event_type = Column(String(100), index=True, nullable=False)
    path = Column(String(500), nullable=True)
    value = Column(Integer, nullable=True)
    click_target = Column(String(255), nullable=True)
    event_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    visitor_session = relationship("VisitorSession", back_populates="visitor_events")


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), unique=True, nullable=False)
    score = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    lead = relationship("Lead", back_populates="score")


class Domain(Base):
    __tablename__ = "domains"

    domain_name = Column(String, primary_key=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
