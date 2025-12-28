from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Newspaper
from app.models.schemas import NewspaperResponse

router = APIRouter(prefix="/api/newspapers", tags=["newspapers"])

@router.get("/", response_model=list[NewspaperResponse])
def get_newspapers(db: Session = Depends(get_db)):
    newspapers = db.query(Newspaper).filter(Newspaper.is_active == True).all()
    return newspapers

@router.get("/{newspaper_id}", response_model=NewspaperResponse)
def get_newspaper(newspaper_id: int, db: Session = Depends(get_db)):
    newspaper = db.query(Newspaper).filter(Newspaper.id == newspaper_id).first()
    if not newspaper:
        raise HTTPException(status_code=404, detail="Newspaper not found")
    return newspaper

@router.get("/language/{language}")
def get_newspapers_by_language(language: str, db: Session = Depends(get_db)):
    newspapers = db.query(Newspaper).filter(
        Newspaper.language == language,
        Newspaper.is_active == True
    ).all()
    return newspapers

@router.get("/genre/{genre}")
def get_newspapers_by_genre(genre: str, db: Session = Depends(get_db)):
    newspapers = db.query(Newspaper).filter(
        Newspaper.genre == genre,
        Newspaper.is_active == True
    ).all()
    return newspapers
