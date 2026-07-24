from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.rating_service import RatingService

router = APIRouter(prefix="/ratings", tags=["Ratings"])

class OrderRatingCreate(BaseModel):
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

class ItemRatingCreate(BaseModel):
    menu_item_id: int
    student_id: str
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

@router.post("/order")
def create_order_rating(data: OrderRatingCreate, db: Session = Depends(get_db)):
    rating_record = RatingService.submit_order_rating(db, data.order_id, data.rating, data.review)
    return rating_record

@router.post("/item")
def create_item_rating(data: ItemRatingCreate, db: Session = Depends(get_db)):
    rating_record = RatingService.submit_item_rating(db, data.menu_item_id, data.student_id, data.rating, data.review)
    return rating_record

@router.get("/stall/{stall_id}")
def get_stall_rating(stall_id: int, db: Session = Depends(get_db)):
    return RatingService.get_stall_average_rating(db, stall_id)

@router.get("/item/{item_id}")
def get_item_rating(item_id: int, db: Session = Depends(get_db)):
    return RatingService.get_item_average_rating(db, item_id)
