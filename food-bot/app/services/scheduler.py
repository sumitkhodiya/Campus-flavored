import datetime
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from ..database import SessionLocal
from ..models import Order, OrderItem
from .notification_service import send_whatsapp_message

# Keep track of reminded order IDs to prevent duplicate reminders
REMINDED_ORDER_IDS = set()

def check_and_send_pickup_reminders():
    """
    Background job: Scans active confirmed orders and sends WhatsApp reminders for near-future pickup slots.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        confirmed_orders = db.query(Order).filter(Order.status == "CONFIRMED").all()

        for order in confirmed_orders:
            if order.id in REMINDED_ORDER_IDS:
                continue

            # Send pickup reminder notification
            remind_text = (
                f"⏰ *Pickup Reminder for Order {order.order_code}*\n\n"
                f"Your order is scheduled for pickup at *{order.pickup_time}*!\n"
                "Please arrive at your selected stall on time and present your Order Code! 🍔"
            )
            
            if order.student:
                send_whatsapp_message(order.student.phone_number, remind_text)
                REMINDED_ORDER_IDS.add(order.id)
                print(f"[Scheduler] Dispatched pickup reminder for Order {order.order_code} to {order.student.phone_number}")

    except Exception as e:
        print(f"[Scheduler Error in Pickup Reminders]: {e}")
    finally:
        db.close()

def check_and_auto_complete_orders():
    """
    Background job: Auto-completes orders whose pickup window has passed and triggers rating prompt.
    """
    db: Session = SessionLocal()
    try:
        # Query orders in READY status that can be auto-completed
        ready_orders = db.query(Order).filter(Order.status == "READY").all()

        for order in ready_orders:
            order.status = "COMPLETED"
            db.commit()
            db.refresh(order)

            print(f"[Scheduler] Auto-completed Order {order.order_code}")

            # Trigger WhatsApp rating prompt
            if order.student:
                prompt_text = (
                    f"🎉 Your order *{order.order_code}* is marked *COMPLETED*!\n\n"
                    "How was your food and pickup service? ⭐\n"
                    "Reply *'rate'* to submit your rating & review!"
                )
                send_whatsapp_message(order.student.phone_number, prompt_text)

    except Exception as e:
        print(f"[Scheduler Error in Auto-Complete]: {e}")
    finally:
        db.close()

def start_scheduler():
    """
    Starts the background job scheduler.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_pickup_reminders, 'interval', seconds=60)
    scheduler.add_job(check_and_auto_complete_orders, 'interval', seconds=60)
    scheduler.start()
    print("⏰ Background Job Scheduler started (Reminders & Auto-Complete active every 60s).")
    return scheduler
