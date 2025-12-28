from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.database import get_db
from app.database.models import Subscription, Delivery
from app.models.schemas import SubscriptionResponse
import stripe
import os
from app.database.models import Newspaper, MilkPackage, Payment

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

@router.get("/{user_id}", response_model=list[SubscriptionResponse])
def get_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.is_active == True
    ).all()
    return subscriptions

@router.post("/{subscription_id}/pause")
def pause_subscription(subscription_id: int, pause_days: int = 7, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    from datetime import timedelta
    pause_until = datetime.utcnow() + timedelta(days=pause_days)
    
    subscription.is_paused = True
    subscription.paused_from = datetime.utcnow()
    subscription.paused_until = pause_until
    
    db.commit()
    db.refresh(subscription)
    return {"message": "Subscription paused", "paused_until": pause_until}

@router.post("/{subscription_id}/resume")
def resume_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_paused = False
    subscription.paused_from = None
    subscription.paused_until = None
    
    db.commit()
    db.refresh(subscription)
    return {"message": "Subscription resumed"}

@router.get("/calendar/{user_id}")
def get_delivery_calendar(user_id: int, db: Session = Depends(get_db)):
    deliveries = db.query(Delivery).filter(Delivery.user_id == user_id).all()
    
    calendar = {}
    for delivery in deliveries:
        date_key = delivery.scheduled_date.date().isoformat()
        if date_key not in calendar:
            calendar[date_key] = []
        calendar[date_key].append({
            "id": delivery.id,
            "subscription_id": delivery.subscription_id,
            "status": delivery.status,
            "time": delivery.scheduled_date.time().isoformat()
        })
    
    return calendar


@router.post("/{subscription_id}/toggle-delivery")
def toggle_delivery(subscription_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    """Toggle a delivery for a subscription on a given date (ISO YYYY-MM-DD).
    If a delivery exists for that subscription+date it will be removed, otherwise created.
    """
    date_str = payload.get("date")
    if not date_str:
        raise HTTPException(status_code=400, detail="Missing date (YYYY-MM-DD)")

    try:
        from datetime import datetime
        scheduled_date = datetime.fromisoformat(date_str)
    except Exception:
        # allow date-only strings by parsing as date then setting a default time
        try:
            from datetime import date, time
            d = datetime.fromisoformat(date_str + 'T08:00:00')
            scheduled_date = d
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD or ISO datetime.")

    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # find existing delivery for that subscription and date
    from datetime import date as _date
    target_day = scheduled_date.date()
    existing = db.query(Delivery).filter(
        Delivery.subscription_id == subscription_id,
        Delivery.scheduled_date >= datetime.combine(target_day, datetime.min.time()),
        Delivery.scheduled_date <= datetime.combine(target_day, datetime.max.time())
    ).first()

    if existing:
        # toggle off -> delete
        db.delete(existing)
        db.commit()
        return {"message": "Delivery removed", "date": target_day.isoformat()}
    else:
        # create new delivery (scheduled)
        delivery = Delivery(
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            scheduled_date=scheduled_date,
            status='pending'
        )
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return {"message": "Delivery scheduled", "date": scheduled_date.date().isoformat(), "delivery_id": delivery.id}


from fastapi import Body


@router.post("/")
def create_subscription(payload: dict = Body(...), db: Session = Depends(get_db)):
    user_id = payload.get('user_id')
    newspaper_ids = payload.get('newspaper_ids', [])  # List of newspaper IDs
    milk_package_id = payload.get('milk_package_id')
    frequency = payload.get('frequency', 'monthly')

    # At least one newspaper subscription is mandatory
    if not newspaper_ids or len(newspaper_ids) == 0:
        raise HTTPException(status_code=400, detail="At least one newspaper selection is required")

    # Fetch newspapers
    newspapers = db.query(Newspaper).filter(
        Newspaper.id.in_(newspaper_ids),
        Newspaper.is_active == True
    ).all()
    
    if len(newspapers) != len(newspaper_ids):
        raise HTTPException(status_code=404, detail="One or more newspapers not found")

    milk = None
    if milk_package_id:
        milk = db.query(MilkPackage).filter(MilkPackage.id == milk_package_id, MilkPackage.is_active == True).first()
        if not milk:
            raise HTTPException(status_code=404, detail="Milk package not found")

    # calculate cost based on frequency
    def price_for(entity, freq, is_newspaper=False):
        if not entity:
            return 0
        # For Newspapers, use fixed weekday/weekend pricing: Rs.4 weekdays, Rs.7 weekends
        if is_newspaper:
            wd_rate = 4
            we_rate = 7
            if freq == 'daily':
                return wd_rate
            if freq == 'weekly':
                return wd_rate * 5 + we_rate * 2
            # monthly: compute over next 30 days (precise monthly window)
            from datetime import date, timedelta
            start = date.today()
            days = 30
            wd_count = 0
            we_count = 0
            for i in range(days):
                d = start + timedelta(days=i)
                if d.weekday() < 5:
                    wd_count += 1
                else:
                    we_count += 1
            return wd_rate * wd_count + we_rate * we_count
        # For milk packages and others, fall back to stored prices
        if freq == 'daily':
            return getattr(entity, 'price_daily', 0)
        if freq == 'weekly':
            return getattr(entity, 'price_weekly', 0)
        return getattr(entity, 'price_monthly', 0)

    # Sum prices for all selected newspapers (with is_newspaper=True)
    newspapers_total = sum(price_for(newspaper, frequency, is_newspaper=True) for newspaper in newspapers)
    milk_total = price_for(milk, frequency, is_newspaper=False)
    total = newspapers_total + milk_total

    # Apply 20% discount if milk is included
    if milk:
        total = total * 0.8

    # create subscription
    subscription = Subscription(
        user_id=user_id,
        milk_package_id=milk_package_id,
        frequency=frequency,
        total_cost=total
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Associate all newspapers with subscription
    for newspaper in newspapers:
        subscription.newspapers.append(newspaper)
    db.commit()

    # Try Razorpay first (preferred), fall back to Stripe
    import razorpay
    razorpay_client = razorpay.Client(auth=(os.getenv('RAZORPAY_PUBLIC_KEY', ''), os.getenv('RAZORPAY_SECRET_KEY', '')))
    
    # Try Razorpay order creation
    try:
        razorpay_order = razorpay_client.order.create(
            amount=int(total * 100),  # in paise
            currency='INR',
            notes={'user_id': user_id, 'subscription_id': subscription.id}
        )
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription.id,
            amount=total,
            status='pending',
            stripe_payment_id=razorpay_order['id'],
            payment_method='razorpay'
        )
        db.add(payment)
        db.commit()
        
        return {
            "subscription_id": subscription.id,
            "payment_id": payment.id,
            "razorpay_order_id": razorpay_order['id'],
            "amount": total,
            "payment_method": "razorpay"
        }
    except Exception as e:
        # Fall back to Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),
                currency='inr',
                metadata={'user_id': user_id, 'subscription_id': subscription.id}
            )

            payment = Payment(
                user_id=user_id,
                subscription_id=subscription.id,
                amount=total,
                status='pending',
                stripe_payment_id=intent.id,
                payment_method='stripe'
            )
            db.add(payment)
            db.commit()

            return {"subscription_id": subscription.id, "payment_id": payment.id, "client_secret": intent.client_secret, "amount": total, "payment_method": "stripe"}
        except Exception as e2:
            db.rollback()
            # Both failed; create pending payment without payment processor
            try:
                payment = Payment(
                    user_id=user_id,
                    subscription_id=subscription.id,
                    amount=total,
                    status='pending',
                    stripe_payment_id=None,
                    payment_method='pending'
                )
                db.add(payment)
                db.commit()
                return {"subscription_id": subscription.id, "payment_id": payment.id, "amount": total, "payment_method": "pending", "error": "Payment processor unavailable"}
            except Exception:
                raise HTTPException(status_code=400, detail=str(e2))
