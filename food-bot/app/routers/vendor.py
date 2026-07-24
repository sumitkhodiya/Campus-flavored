from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Vendor, Stall, MenuItem, Order, OrderItem, ItemRating
from ..dependencies import get_current_vendor
from ..services.notification_service import send_whatsapp_message

router = APIRouter(prefix="/vendor", tags=["Vendor"])

class OrderStatusUpdate(BaseModel):
    status: str  # PREPARING, READY, COMPLETED, CANCELLED

class MenuItemCreate(BaseModel):
    name: str
    price: float
    half_price: Optional[float] = None
    available: Optional[bool] = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    half_price: Optional[float] = None
    available: Optional[bool] = None

class StallStatusUpdate(BaseModel):
    is_open: bool

@router.get("/orders")
def get_vendor_orders(current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    orders = db.query(Order).join(OrderItem).join(MenuItem).filter(MenuItem.stall_id == stall_id).distinct().all()
    
    result = []
    for order in orders:
        items = []
        for oi in order.items:
            if oi.menu_item.stall_id == stall_id:
                items.append({
                    "item_id": oi.menu_item_id,
                    "item_name": oi.menu_item.name,
                    "portion": oi.portion,
                    "quantity": oi.quantity,
                    "price": oi.menu_item.half_price if (oi.portion == "HALF" and oi.menu_item.half_price) else oi.menu_item.price
                })
        result.append({
            "order_id": order.id,
            "order_code": order.order_code,
            "student_id": order.student_id,
            "status": order.status,
            "pickup_time": order.pickup_time,
            "created_at": order.created_at,
            "items": items
        })
    return {"stall_id": stall_id, "orders": result}

@router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, payload: OrderStatusUpdate, current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    new_status = payload.status.upper()
    if new_status not in ["PENDING", "CONFIRMED", "PREPARING", "READY", "COMPLETED", "CANCELLED"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value")

    order.status = new_status
    db.commit()
    db.refresh(order)

    # Automated trigger: When marked COMPLETED, send WhatsApp rating prompt
    if new_status == "COMPLETED" and order.student:
        prompt_text = (
            f"🎉 Your order *{order.order_code}* is marked *COMPLETED*!\n\n"
            "How was your food and pickup service? ⭐\n"
            "Reply *'rate'* to submit your rating & review!"
        )
        send_whatsapp_message(order.student.phone_number, prompt_text)

    return {"order_id": order.id, "order_code": order.order_code, "new_status": order.status}

@router.get("/menu-items")
def get_vendor_menu(current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    items = db.query(MenuItem).filter(MenuItem.stall_id == stall_id).all()
    return {"stall_id": stall_id, "total_items": len(items), "menu_items": items}

@router.post("/menu-items")
def create_menu_item(item_data: MenuItemCreate, current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    db_item = MenuItem(
        stall_id=stall_id,
        name=item_data.name,
        price=item_data.price,
        half_price=item_data.half_price,
        available=item_data.available
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/menu-items/{item_id}")
def update_menu_item(item_id: int, item_data: MenuItemUpdate, current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.stall_id == stall_id).first()
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found in vendor stall")

    if item_data.name is not None:
        db_item.name = item_data.name
    if item_data.price is not None:
        db_item.price = item_data.price
    if item_data.half_price is not None:
        db_item.half_price = item_data.half_price
    if item_data.available is not None:
        db_item.available = item_data.available

    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/menu-items/{item_id}")
def delete_menu_item(item_id: int, current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.stall_id == stall_id).first()
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found in vendor stall")

    db.delete(db_item)
    db.commit()
    return {"message": f"Menu item #{item_id} deleted successfully"}

@router.patch("/stall/status")
def toggle_stall_status(status_data: StallStatusUpdate, current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    stall = db.query(Stall).filter(Stall.id == stall_id).first()
    if not stall:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stall not found")

    stall.is_open = status_data.is_open
    db.commit()
    db.refresh(stall)
    return {"stall_id": stall.id, "stall_name": stall.name, "is_open": stall.is_open}

@router.get("/ratings")
def get_vendor_ratings(current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    ratings = db.query(ItemRating).join(MenuItem).filter(MenuItem.stall_id == stall_id).all()
    avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0.0
    return {
        "stall_id": stall_id,
        "average_rating": round(avg_rating, 2),
        "total_reviews": len(ratings),
        "ratings": ratings
    }

@router.get("/sales")
def get_vendor_sales(current_vendor: dict = Depends(get_current_vendor), db: Session = Depends(get_db)):
    stall_id = current_vendor["stall_id"]
    order_items = db.query(OrderItem).join(MenuItem).filter(MenuItem.stall_id == stall_id).all()
    
    total_sales = 0.0
    items_sold_count = 0
    item_breakdown = {}

    for oi in order_items:
        price = oi.menu_item.half_price if (oi.portion == "HALF" and oi.menu_item.half_price) else oi.menu_item.price
        subtotal = price * oi.quantity
        total_sales += subtotal
        items_sold_count += oi.quantity
        
        item_name = oi.menu_item.name
        item_breakdown[item_name] = item_breakdown.get(item_name, 0) + oi.quantity

    return {
        "stall_id": stall_id,
        "total_revenue": round(total_sales, 2),
        "total_items_sold": items_sold_count,
        "item_breakdown": item_breakdown
    }
