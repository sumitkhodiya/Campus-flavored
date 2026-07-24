import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Stall, Order, OrderItem, MenuItem, ItemRating, OrderRating

class AnalyticsService:
    @staticmethod
    def get_admin_stall_summary(db: Session) -> list:
        stalls = db.query(Stall).all()
        today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        summary = []
        for stall in stalls:
            # Total menu items
            menu_count = db.query(func.count(MenuItem.id)).filter(MenuItem.stall_id == stall.id).scalar() or 0
            
            # Today's order count
            today_orders = db.query(func.count(Order.id.distinct())).join(OrderItem).join(MenuItem).filter(
                MenuItem.stall_id == stall.id,
                Order.created_at >= today_start
            ).scalar() or 0

            # Total order count
            total_orders = db.query(func.count(Order.id.distinct())).join(OrderItem).join(MenuItem).filter(
                MenuItem.stall_id == stall.id
            ).scalar() or 0

            # Total revenue
            order_items = db.query(OrderItem).join(MenuItem).filter(MenuItem.stall_id == stall.id).all()
            total_revenue = 0.0
            for oi in order_items:
                price = oi.menu_item.half_price if (oi.portion == "HALF" and oi.menu_item.half_price) else oi.menu_item.price
                total_revenue += price * oi.quantity

            summary.append({
                "stall_id": stall.id,
                "stall_name": stall.name,
                "location": stall.location,
                "is_open": stall.is_open,
                "menu_items_count": menu_count,
                "today_orders_count": today_orders,
                "total_orders_count": total_orders,
                "total_revenue": round(total_revenue, 2)
            })

        return summary

    @staticmethod
    def get_admin_sales_analytics(db: Session, stall_id: int = None, start_date: str = None, end_date: str = None) -> dict:
        query = db.query(OrderItem).join(MenuItem).join(Order)
        
        if stall_id:
            query = query.filter(MenuItem.stall_id == stall_id)

        if start_date:
            try:
                dt_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(Order.created_at >= dt_start)
            except ValueError:
                pass

        if end_date:
            try:
                dt_end = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)
                query = query.filter(Order.created_at < dt_end)
            except ValueError:
                pass

        order_items = query.all()

        total_revenue = 0.0
        total_items_sold = 0
        stall_breakdown = {}

        for oi in order_items:
            price = oi.menu_item.half_price if (oi.portion == "HALF" and oi.menu_item.half_price) else oi.menu_item.price
            subtotal = price * oi.quantity
            total_revenue += subtotal
            total_items_sold += oi.quantity

            stall_name = oi.menu_item.stall.name
            if stall_name not in stall_breakdown:
                stall_breakdown[stall_name] = {"items_sold": 0, "revenue": 0.0}
            
            stall_breakdown[stall_name]["items_sold"] += oi.quantity
            stall_breakdown[stall_name]["revenue"] = round(stall_breakdown[stall_name]["revenue"] + subtotal, 2)

        return {
            "filters": {
                "stall_id": stall_id,
                "start_date": start_date,
                "end_date": end_date
            },
            "total_revenue": round(total_revenue, 2),
            "total_items_sold": total_items_sold,
            "stall_breakdown": stall_breakdown
        }

    @staticmethod
    def get_admin_flagged_ratings(db: Session, threshold: float = 3.0) -> dict:
        flagged_order_ratings = db.query(OrderRating).filter(OrderRating.rating < threshold).all()
        flagged_item_ratings = db.query(ItemRating).filter(ItemRating.rating < threshold).all()

        order_flags = []
        for r in flagged_order_ratings:
            order_flags.append({
                "rating_id": r.id,
                "order_id": r.order_id,
                "order_code": r.order.order_code,
                "rating": r.rating,
                "review": r.review,
                "created_at": r.created_at
            })

        item_flags = []
        for r in flagged_item_ratings:
            item_flags.append({
                "rating_id": r.id,
                "menu_item_id": r.menu_item_id,
                "item_name": r.menu_item.name,
                "stall_name": r.menu_item.stall.name,
                "student_id": r.student_id,
                "rating": r.rating,
                "review": r.review,
                "created_at": r.created_at
            })

        return {
            "threshold": threshold,
            "total_flagged_order_ratings": len(order_flags),
            "total_flagged_item_ratings": len(item_flags),
            "flagged_order_ratings": order_flags,
            "flagged_item_ratings": item_flags
        }
