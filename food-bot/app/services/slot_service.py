from sqlalchemy.orm import Session
from ..models import Slot

class SlotService:
    @staticmethod
    def get_slots_by_stall(db: Session, stall_id: int):
        return db.query(Slot).filter(Slot.stall_id == stall_id, Slot.capacity > 0).all()

    @staticmethod
    def get_slot_by_id(db: Session, slot_id: int):
        return db.query(Slot).filter(Slot.id == slot_id).first()

    @staticmethod
    def reserve_slot(db: Session, slot_id: int) -> bool:
        slot = db.query(Slot).filter(Slot.id == slot_id).first()
        if slot and slot.capacity > 0:
            slot.capacity -= 1
            db.commit()
            db.refresh(slot)
            return True
        return False
