from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import MilkPackage
from app.models.schemas import MilkPackageResponse

router = APIRouter(prefix="/api/milk", tags=["milk"])

@router.get("/", response_model=list[MilkPackageResponse])
def get_milk_packages(db: Session = Depends(get_db)):
    packages = db.query(MilkPackage).filter(MilkPackage.is_active == True).all()
    return packages

@router.get("/{package_id}", response_model=MilkPackageResponse)
def get_milk_package(package_id: int, db: Session = Depends(get_db)):
    package = db.query(MilkPackage).filter(MilkPackage.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Milk package not found")
    return package
