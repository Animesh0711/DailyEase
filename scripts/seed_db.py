import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.database.database import SessionLocal
from app.database import models


def seed():
    db = SessionLocal()
    try:
        if db.query(models.Newspaper).count() == 0:
            english = [
                {"name": "Times of India", "language": "English", "genre": "General", "price_daily": 5, "price_weekly": 30, "price_monthly": 120, "description": "Leading English daily"},
                {"name": "Hindustan Times", "language": "English", "genre": "General", "price_daily": 5, "price_weekly": 30, "price_monthly": 120, "description": "Trusted English newspaper"},
                {"name": "Economic Times", "language": "English", "genre": "Business", "price_daily": 8, "price_weekly": 50, "price_monthly": 200, "description": "Business & markets"}
            ]
            marathi = [
                {"name": "Lokmat", "language": "Marathi", "genre": "General", "price_daily": 4, "price_weekly": 25, "price_monthly": 100, "description": "Popular Marathi daily"},
                {"name": "Sakal", "language": "Marathi", "genre": "General", "price_daily": 4, "price_weekly": 25, "price_monthly": 100, "description": "Regional news and more"},
                {"name": "Lokshahir", "language": "Marathi", "genre": "General", "price_daily": 3.5, "price_weekly": 20, "price_monthly": 80, "description": "Local coverage"},
                {"name": "Pune Times", "language": "Marathi", "genre": "General", "price_daily": 3.5, "price_weekly": 20, "price_monthly": 80, "description": "Pune local news"},
                {"name": "Pudhari", "language": "Marathi", "genre": "General", "price_daily": 4, "price_weekly": 24, "price_monthly": 95, "description": "Marathi daily"}
            ]
            for item in english + marathi:
                db.add(models.Newspaper(**item))
            db.commit()
        if db.query(models.MilkPackage).count() == 0:
            milk_pkgs = [
                {"name": "500ml", "quantity_ml": 500, "price_daily": 20, "price_weekly": 120, "price_monthly": 400, "description": "Fresh 500ml pack"},
                {"name": "1L", "quantity_ml": 1000, "price_daily": 35, "price_weekly": 210, "price_monthly": 700, "description": "1 litre pack"},
                {"name": "2L", "quantity_ml": 2000, "price_daily": 65, "price_weekly": 390, "price_monthly": 1300, "description": "2 litre family pack"}
            ]
            for m in milk_pkgs:
                db.add(models.MilkPackage(**m))
            db.commit()
        print('Seed complete')
    finally:
        db.close()

if __name__ == '__main__':
    seed()
