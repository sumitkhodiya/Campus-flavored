from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Vendor, Stall
from ..dependencies import get_current_admin
from ..services.analytics_service import AnalyticsService
from ..auth_utils import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])

class VendorCreateRequest(BaseModel):
    name: str
    email: str
    password: str
    stall_id: int

@router.get("/stalls")
def get_all_stalls_summary(current_admin: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    summary = AnalyticsService.get_admin_stall_summary(db)
    return {"total_stalls": len(summary), "stalls": summary}

@router.get("/sales")
def get_sales_analytics(
    stall_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_admin_sales_analytics(db, stall_id=stall_id, start_date=start_date, end_date=end_date)

@router.get("/ratings")
def get_ratings_analytics(
    threshold: float = Query(3.0, description="Flag ratings below this threshold"),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_admin_flagged_ratings(db, threshold=threshold)

@router.post("/vendors")
def create_vendor_account(
    vendor_data: VendorCreateRequest,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Verify stall exists
    stall = db.query(Stall).filter(Stall.id == vendor_data.stall_id).first()
    if not stall:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stall ID not found")

    # Check existing email
    existing = db.query(Vendor).filter(Vendor.email == vendor_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vendor email already exists")

    vendor = Vendor(
        name=vendor_data.name,
        email=vendor_data.email,
        hashed_password=get_password_hash(vendor_data.password),
        stall_id=vendor_data.stall_id
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    return {
        "vendor_id": vendor.id,
        "name": vendor.name,
        "email": vendor.email,
        "stall_id": vendor.stall_id,
        "stall_name": stall.name
    }
