from typing import Optional

from fastapi import APIRouter, Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import schemas
from app.core.auth import decode_token
from app.core.database import get_db
from app.services import payment_service

router = APIRouter()
security = HTTPBearer()


@router.post("/initpayment_Basic")
def init_payment_basic(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return payment_service.init_payment_basic(user_id, db)


@router.post("/initpayment_Pro")
def init_payment_pro(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return payment_service.init_payment_pro(user_id, db)


@router.post("/paymentorder")
def create_order(
    order_data: schemas.OrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return payment_service.create_order(user_id, order_data, db)


@router.post("/verifypayment")
def verify_payment(
    payment: schemas.PaymentVerification,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    user_id = decode_token(credentials.credentials)["sub"]
    return payment_service.verify_payment(user_id, payment, db)


@router.post("/webhooks/blazerpay")
async def handle_blazerpay_webhook(
    request: Request,
    x_blazerpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    return await payment_service.handle_blazerpay_webhook(request, x_blazerpay_signature, db)
