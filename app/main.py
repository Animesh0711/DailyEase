from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, newspapers, milk, subscriptions, payments, magazines
from app.routes import admin
from app.routes import calendar as calendar_router
from app.database.database import Base, engine
import os
from sqlalchemy.orm import Session
from app.database import models
from app.database.database import SessionLocal
import logging

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DailyEaze",
    description="Newspaper & Milk Delivery Management Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(auth.router)
app.include_router(newspapers.router)
app.include_router(milk.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(magazines.router)
app.include_router(admin.router)
app.include_router(calendar_router.router)


@app.get('/api/config')
def get_config():
    return {
        "stripe_public_key": os.getenv('STRIPE_PUBLIC_KEY', ''),
        "razorpay_public_key": os.getenv('RAZORPAY_PUBLIC_KEY', '')
    }


@app.on_event("startup")
def seed_initial_data():
    db: Session = SessionLocal()
    try:
        # Seed newspapers if none exist
        count = db.query(models.Newspaper).count()
        if count == 0:
            # English: General and Business (no Sports)
            english = [
                {"name": "Times of India", "language": "English", "genre": "General", "price_daily": 5, "price_weekly": 30, "price_monthly": 120, "description": "Leading English daily"},
                {"name": "Hindustan Times", "language": "English", "genre": "General", "price_daily": 5, "price_weekly": 30, "price_monthly": 120, "description": "Trusted English newspaper"},
                {"name": "Economic Times", "language": "English", "genre": "Business", "price_daily": 8, "price_weekly": 50, "price_monthly": 200, "description": "Business & markets"}
            ]

            # Marathi: only General
            marathi = [
                {"name": "Lokmat", "language": "Marathi", "genre": "General", "price_daily": 4, "price_weekly": 25, "price_monthly": 100, "description": "Popular Marathi daily"},
                {"name": "Sakal", "language": "Marathi", "genre": "General", "price_daily": 4, "price_weekly": 25, "price_monthly": 100, "description": "Regional news and more"},
                {"name": "Lokshahir", "language": "Marathi", "genre": "General", "price_daily": 3.5, "price_weekly": 20, "price_monthly": 80, "description": "Local coverage"},
                {"name": "Pune Times", "language": "Marathi", "genre": "General", "price_daily": 3.5, "price_weekly": 20, "price_monthly": 80, "description": "Pune local news"},
                {"name": "Pudhari", "language": "Marathi", "genre": "General", "price_daily": 4, "price_weekly": 24, "price_monthly": 95, "description": "Marathi daily"}
            ]

            for item in english + marathi:
                n = models.Newspaper(**item)
                db.add(n)

            # Seed a few milk packages if none exist
            if db.query(models.MilkPackage).count() == 0:
                milk_pkgs = [
                    {"name": "500ml", "quantity_ml": 500, "price_daily": 20, "price_weekly": 120, "price_monthly": 400, "description": "Fresh 500ml pack"},
                    {"name": "1L", "quantity_ml": 1000, "price_daily": 35, "price_weekly": 210, "price_monthly": 700, "description": "1 litre pack"},
                    {"name": "2L", "quantity_ml": 2000, "price_daily": 65, "price_weekly": 390, "price_monthly": 1300, "description": "2 litre family pack"}
                ]
                for m in milk_pkgs:
                    db.add(models.MilkPackage(**m))

            db.commit()
    except Exception as e:
        logging.exception("Failed to seed initial data: %s", e)
        db.rollback()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to DailyEaze API",
        "docs": "/docs",
        "version": "1.0.0"
    }
