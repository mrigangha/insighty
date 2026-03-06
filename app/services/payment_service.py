import hashlib
import hmac
import json
import os

import razorpay
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app import schemas
from app.repositories import user_repo

razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID", "rzp_test_RznNlAeuXL0d3K"), os.getenv("RAZORPAY_KEY_SECRET", "quzU643RrL3EC6pEbQHzOUc3"))
)

BLAZERPAY_WEBHOOK_SECRET = os.getenv("BLAZERPAY_WEBHOOK_SECRET", "virvir123")


def init_payment_basic(user_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user_repo.set_payment_status(db, user, "Basic_PaymentOrder")
    return {"status": user.payment_status}


def init_payment_pro(user_id: int, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user_repo.set_payment_status(db, user, "Premium_PaymentOrder")
    return {"status": user.payment_status}


def create_order(user_id: int, order_data: schemas.OrderRequest, db: Session) -> dict:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if order_data.amount == 0:
        raise HTTPException(status_code=400, detail="Free plan doesn't require payment")

    try:
        order = razorpay_client.order.create({
            "amount": order_data.amount,
            "currency": order_data.currency,
            "payment_capture": 1,
            "notes": {"plan": order_data.plan, "user_id": user_id},
        })
        user_repo.set_order(db, user, order_data.plan, order["id"])
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


def verify_payment(user_id: int, payment: schemas.PaymentVerification, db: Session) -> dict:
    try:
        params_dict = {
            "razorpay_order_id": payment.razorpay_order_id,
            "razorpay_payment_id": payment.razorpay_payment_id,
            "razorpay_signature": payment.razorpay_signature,
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        payment_details = razorpay_client.payment.fetch(payment.razorpay_payment_id)

        user = user_repo.get_by_id(db, user_id)
        user_repo.set_payment_captured(db, user, payment.razorpay_payment_id, payment.razorpay_order_id)

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")


def _verify_blazerpay_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(BLAZERPAY_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


async def handle_blazerpay_webhook(request: Request, x_blazerpay_signature: str | None, db: Session) -> dict:
    raw_body = await request.body()

    if BLAZERPAY_WEBHOOK_SECRET != "virvir123":
        if not x_blazerpay_signature or not _verify_blazerpay_signature(raw_body, x_blazerpay_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(raw_body)
    event = payload.get("event")
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    email = entity.get("email")

    if event == "payment.captured":
        user = user_repo.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_repo.set_payment_captured(db, user, entity.get("id"), entity.get("order_id"))

    elif event == "payment.failed":
        user = user_repo.get_by_email(db, email)
        if user:
            user_repo.set_payment_failed(db, user)

    return {"status": "received"}
