from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class Student(Base):
    __tablename__ = "students"

    reg_number = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)

    orders = relationship("Order", back_populates="student")
    item_ratings = relationship("ItemRating", back_populates="student")

class Stall(Base):
    __tablename__ = "stalls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    is_open = Column(Boolean, default=True)

    menu_items = relationship("MenuItem", back_populates="stall")
    slots = relationship("Slot", back_populates="stall")
    vendors = relationship("Vendor", back_populates="stall")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    stall_id = Column(Integer, ForeignKey("stalls.id"), nullable=True)

    stall = relationship("Stall", back_populates="vendors")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    stall_id = Column(Integer, ForeignKey("stalls.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)        # Full price of the dish
    half_price = Column(Float, nullable=True)     # Optional Half price if available
    available = Column(Boolean, default=True)

    stall = relationship("Stall", back_populates="menu_items")
    ratings = relationship("ItemRating", back_populates="menu_item")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String, unique=True, index=True, nullable=True)
    student_id = Column(String, ForeignKey("students.reg_number"), nullable=False)
    status = Column(String, default="PENDING")   # PENDING, CONFIRMED, PREPARING, READY, COMPLETED, CANCELLED
    pickup_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    order_rating = relationship("OrderRating", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    portion = Column(String, default="FULL")     # "FULL" or "HALF"

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")

class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(String, nullable=False)
    capacity = Column(Integer, default=10)
    stall_id = Column(Integer, ForeignKey("stalls.id"), nullable=False)

    stall = relationship("Stall", back_populates="slots")

class OrderRating(Base):
    __tablename__ = "order_ratings"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)     # 1 to 5 stars
    review = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    order = relationship("Order", back_populates="order_rating")

class ItemRating(Base):
    __tablename__ = "item_ratings"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    student_id = Column(String, ForeignKey("students.reg_number"), nullable=False)
    rating = Column(Integer, nullable=False)     # 1 to 5 stars
    review = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    menu_item = relationship("MenuItem", back_populates="ratings")
    student = relationship("Student", back_populates="item_ratings")
