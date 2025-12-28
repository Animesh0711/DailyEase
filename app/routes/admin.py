from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Newspaper, MilkPackage
from app.models.schemas import NewspaperResponse, MilkPackageResponse

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post('/newspapers')
def create_newspaper(payload: dict, db: Session = Depends(get_db)):
    n = Newspaper(**payload)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n

@router.put('/newspapers/{id}')
def update_newspaper(id: int, payload: dict, db: Session = Depends(get_db)):
    n = db.query(Newspaper).filter(Newspaper.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail='Newspaper not found')
    for k, v in payload.items():
        setattr(n, k, v)
    db.commit()
    db.refresh(n)
    return n

@router.delete('/newspapers/{id}')
def delete_newspaper(id: int, db: Session = Depends(get_db)):
    n = db.query(Newspaper).filter(Newspaper.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail='Newspaper not found')
    n.is_active = False
    db.commit()
    return {'message':'Newspaper deactivated'}

# Milk package CRUD
@router.post('/milk')
def create_milk(payload: dict, db: Session = Depends(get_db)):
    m = MilkPackage(**payload)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@router.put('/milk/{id}')
def update_milk(id: int, payload: dict, db: Session = Depends(get_db)):
    m = db.query(MilkPackage).filter(MilkPackage.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail='Milk package not found')
    for k, v in payload.items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m

@router.delete('/milk/{id}')
def delete_milk(id: int, db: Session = Depends(get_db)):
    m = db.query(MilkPackage).filter(MilkPackage.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail='Milk package not found')
    m.is_active = False
    db.commit()
    return {'message':'Milk package deactivated'}
