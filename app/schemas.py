from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    amount: int
    currency: str = "INR"
    plan: str


class PaymentVerification(BaseModel):
    razorpay_order_id: str = Field(..., description="Order ID from Razorpay")
    razorpay_payment_id: str = Field(..., description="Payment ID from Razorpay")
    razorpay_signature: str = Field(..., description="Signature from Razorpay")

    class Config:
        schema_extra = {
            "example": {
                "razorpay_order_id": "order_abc123xyz",
                "razorpay_payment_id": "pay_xyz789abc",
                "razorpay_signature": "a1b2c3d4e5f6...",
            }
        }


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    pricing: Optional[str] = "Free"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class ProjectCreate(BaseModel):
    name: str
    domain: str


class LeadCreate(BaseModel):
    name: str
    email: str
    phone: str
    source: str
    status: str
    project_id: int


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None


class LeadRead(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    source: str


class SessionCreate(BaseModel):
    session_id: str
    tracking_key: str


class VisitorEventIn(BaseModel):
    session_id: str
    event_type: str
    tracking_key: str
    path: str | None = None
    value: int | None = None
    click_target: Optional[str] = None
