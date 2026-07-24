from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

postgres_url = os.getenv("POSTGRES_DATABASE_URL")
sqlite_url = "sqlite:///./food_bot.db"

engine = None

if postgres_url and postgres_url.startswith("postgresql"):
    try:
        temp_engine = create_engine(postgres_url)
        conn = temp_engine.connect()
        conn.close()
        engine = temp_engine
        print(f"Connected to PostgreSQL database: {postgres_url}")
    except Exception as e:
        print(f"PostgreSQL unavailable ({e}). Falling back to SQLite database.")

if engine is None:
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    print("Using SQLite database: food_bot.db")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def initialize_database():
    Base.metadata.create_all(bind=engine)

    from .auth_utils import get_password_hash
    from .models import ItemRating, MenuItem, Order, OrderItem, OrderRating, Slot, Stall, Student, Vendor

    db = SessionLocal()
    try:
        if db.query(Stall).count() > 0:
            return

        stall = Stall(name="Campus Tiffin", location="Main Canteen", is_open=True)
        db.add(stall)
        db.flush()

        vendor = Vendor(
            name="Tiffin Manager",
            email="vendor@campus.edu",
            hashed_password=get_password_hash("vendor123"),
            stall_id=stall.id,
        )
        admin = Vendor(
            name="Campus Admin",
            email="admin@campus.edu",
            hashed_password=get_password_hash("admin123"),
            stall_id=None,
        )
        db.add_all([vendor, admin])

        student = Student(
            reg_number="2023CS099",
            name="Rahul Sharma",
            phone_number="+919876543210",
        )
        db.add(student)
        db.flush()

        menu_items = [
            MenuItem(stall_id=stall.id, name="Veg Biryani", price=120.0, half_price=70.0, available=True),
            MenuItem(stall_id=stall.id, name="Paneer Wrap", price=90.0, half_price=55.0, available=True),
            MenuItem(stall_id=stall.id, name="Masala Dosa", price=80.0, half_price=45.0, available=True),
        ]
        db.add_all(menu_items)
        db.flush()

        slots = [
            Slot(stall_id=stall.id, time="12:00 PM - 12:30 PM", capacity=8),
            Slot(stall_id=stall.id, time="01:00 PM - 01:30 PM", capacity=6),
            Slot(stall_id=stall.id, time="06:00 PM - 06:30 PM", capacity=10),
        ]
        db.add_all(slots)
        db.flush()

        order = Order(
            student_id=student.reg_number,
            order_code="ORD-8821",
            status="COMPLETED",
            pickup_time="01:00 PM - 01:30 PM",
        )
        db.add(order)
        db.flush()

        db.add(OrderItem(order_id=order.id, menu_item_id=menu_items[0].id, quantity=2, portion="FULL"))
        db.add(OrderRating(order_id=order.id, rating=5, review="Super fast pickup and fresh food!"))
        db.add(ItemRating(menu_item_id=menu_items[0].id, student_id=student.reg_number, rating=5, review="Delicious!"))

        db.commit()
        print("Initialized local demo data for the food bot.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
