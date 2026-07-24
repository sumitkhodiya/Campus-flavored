import random
import string
from sqlalchemy.orm import Session
from ..models import Order, OrderItem, MenuItem

class OrderService:
    @staticmethod
    def generate_order_code() -> str:
        digits = ''.join(random.choices(string.digits, k=4))
        return f"ORD-{digits}"

    @staticmethod
    def create_confirmed_order(db: Session, student_id: str, items_draft: list, pickup_time: str) -> Order:
        order_code = OrderService.generate_order_code()
        
        order = Order(
            order_code=order_code,
            student_id=student_id,
            status="CONFIRMED",
            pickup_time=pickup_time
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        for draft in items_draft:
            item_id = draft["menu_item_id"]
            qty = draft.get("quantity", 1)
            portion = draft.get("portion", "FULL")

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_id,
                quantity=qty,
                portion=portion
            )
            db.add(order_item)
            
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def calculate_order_total(order: Order) -> float:
        total = 0.0
        for oi in order.items:
            price = oi.menu_item.half_price if (oi.portion == "HALF" and oi.menu_item.half_price) else oi.menu_item.price
            total += price * oi.quantity
        return total

    @staticmethod
    def get_student_active_orders(db: Session, student_id: str):
        return db.query(Order).filter(
            Order.student_id == student_id,
            Order.status.in_(["PENDING", "CONFIRMED", "PREPARING", "READY"])
        ).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_student_order_history(db: Session, student_id: str):
        return db.query(Order).filter(
            Order.student_id == student_id
        ).order_by(Order.created_at.desc()).all()

    @staticmethod
    def cancel_order(db: Session, order_id: int) -> bool:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order and order.status in ["PENDING", "CONFIRMED"]:
            order.status = "CANCELLED"
            db.commit()
            return True
        return False
