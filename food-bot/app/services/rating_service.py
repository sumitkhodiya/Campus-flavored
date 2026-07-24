from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import OrderRating, ItemRating, MenuItem, Order

class RatingService:
    @staticmethod
    def submit_order_rating(db: Session, order_id: int, rating: int, review: str = None) -> OrderRating:
        existing = db.query(OrderRating).filter(OrderRating.order_id == order_id).first()
        if existing:
            existing.rating = rating
            existing.review = review
            db.commit()
            db.refresh(existing)
            return existing

        order_rating = OrderRating(
            order_id=order_id,
            rating=rating,
            review=review
        )
        db.add(order_rating)
        db.commit()
        db.refresh(order_rating)
        return order_rating

    @staticmethod
    def submit_item_rating(db: Session, menu_item_id: int, student_id: str, rating: int, review: str = None) -> ItemRating:
        existing = db.query(ItemRating).filter(
            ItemRating.menu_item_id == menu_item_id,
            ItemRating.student_id == student_id
        ).first()

        if existing:
            existing.rating = rating
            existing.review = review
            db.commit()
            db.refresh(existing)
            return existing

        item_rating = ItemRating(
            menu_item_id=menu_item_id,
            student_id=student_id,
            rating=rating,
            review=review
        )
        db.add(item_rating)
        db.commit()
        db.refresh(item_rating)
        return item_rating

    @staticmethod
    def get_stall_average_rating(db: Session, stall_id: int) -> dict:
        # Query average rating across stall's menu items
        result = db.query(
            func.avg(ItemRating.rating).label("avg_rating"),
            func.count(ItemRating.id).label("total_ratings")
        ).join(MenuItem).filter(MenuItem.stall_id == stall_id).first()

        avg_rating = float(result.avg_rating) if result and result.avg_rating else 0.0
        total_ratings = int(result.total_ratings) if result and result.total_ratings else 0

        return {
            "stall_id": stall_id,
            "average_rating": round(avg_rating, 2),
            "total_ratings": total_ratings
        }

    @staticmethod
    def get_item_average_rating(db: Session, menu_item_id: int) -> dict:
        result = db.query(
            func.avg(ItemRating.rating).label("avg_rating"),
            func.count(ItemRating.id).label("total_ratings")
        ).filter(ItemRating.menu_item_id == menu_item_id).first()

        avg_rating = float(result.avg_rating) if result and result.avg_rating else 0.0
        total_ratings = int(result.total_ratings) if result and result.total_ratings else 0

        return {
            "menu_item_id": menu_item_id,
            "average_rating": round(avg_rating, 2),
            "total_ratings": total_ratings
        }
