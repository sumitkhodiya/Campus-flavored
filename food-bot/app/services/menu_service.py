from sqlalchemy.orm import Session
from typing import Optional
from ..models import MenuItem

class MenuService:
    @staticmethod
    def get_all_items(db: Session):
        return db.query(MenuItem).filter(MenuItem.available == True).all()

    @staticmethod
    def get_items_by_stall(db: Session, stall_id: int):
        return db.query(MenuItem).filter(MenuItem.stall_id == stall_id, MenuItem.available == True).all()

    @staticmethod
    def get_item_by_name(db: Session, name: str):
        return db.query(MenuItem).filter(MenuItem.name == name).first()

    @staticmethod
    def get_item_by_id(db: Session, item_id: int):
        return db.query(MenuItem).filter(MenuItem.id == item_id).first()

    @staticmethod
    def create_menu_item(db: Session, stall_id: int, name: str, price: float, half_price: Optional[float] = None, available: bool = True):
        db_item = MenuItem(stall_id=stall_id, name=name, price=price, half_price=half_price, available=available)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
