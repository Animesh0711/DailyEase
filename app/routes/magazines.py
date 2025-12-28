from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Magazine
from app.models.schemas import MagazineResponse

router = APIRouter(prefix="/api/magazines", tags=["magazines"])

@router.get("/", response_model=list[MagazineResponse])
def get_magazines(db: Session = Depends(get_db)):
    magazines = db.query(Magazine).filter(Magazine.is_active == True).all()
    return magazines

@router.get("/complementary/{language}")
def get_complementary_magazines(language: str, db: Session = Depends(get_db)):
    magazines = db.query(Magazine).filter(
        Magazine.language == language,
        Magazine.is_complementary == True,
        Magazine.is_active == True
    ).all()
    return magazines
