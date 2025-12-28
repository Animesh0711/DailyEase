from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Payment
from app.models.schemas import PaymentResponse
import stripe
import os
import razorpay
import hashlib
import hmac

router = APIRouter(prefix="/api/payments", tags=["payments"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_key_here")

@router.post("/create-payment-intent")
def create_payment_intent(amount: float, user_id: int, subscription_id: int = None, db: Session = Depends(get_db)):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency="inr",
            metadata={"user_id": user_id, "subscription_id": subscription_id}
        )
        
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            status="pending",
            stripe_payment_id=intent.id,
            payment_method="stripe"
        )
        db.add(payment)
        db.commit()
        
        return {"client_secret": intent.client_secret, "payment_id": payment.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm-payment/{payment_id}")
def confirm_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    try:
        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_id)
        
        if intent.status == "succeeded":
            payment.status = "completed"
            from datetime import datetime
            payment.completed_at = datetime.utcnow()
            db.commit()
            return {"status": "Payment completed successfully"}
        else:
            payment.status = "failed"
            db.commit()
            raise HTTPException(status_code=400, detail="Payment failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history/{user_id}", response_model=list[PaymentResponse])
def get_payment_history(user_id: int, db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    return payments

@router.post("/verify-razorpay")
def verify_razorpay_payment(payload: dict = Body(...), db: Session = Depends(get_db)):
    """Verify Razorpay payment signature and mark payment as completed."""
    payment_id = payload.get('payment_id')
    razorpay_payment_id = payload.get('razorpay_payment_id')
    razorpay_order_id = payload.get('razorpay_order_id')
    razorpay_signature = payload.get('razorpay_signature')
    
    if not all([payment_id, razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        raise HTTPException(status_code=400, detail="Missing Razorpay payment details")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify signature
    secret = os.getenv('RAZORPAY_SECRET_KEY', '')
    if not secret:
        raise HTTPException(status_code=400, detail="Razorpay not configured")
    
    data_to_verify = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected_signature = hmac.new(
        secret.encode(),
        data_to_verify.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if expected_signature != razorpay_signature:
        payment.status = 'failed'
        db.commit()
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # Mark as completed
    from datetime import datetime
    payment.status = 'completed'
    payment.completed_at = datetime.utcnow()
    db.commit()
    
    return {"status": "Payment verified and completed successfully"}