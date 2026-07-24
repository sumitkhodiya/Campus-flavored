from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Vendor
from ..auth_utils import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    stall_id: int | None = None

@router.post("/login", response_model=TokenResponse)
def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    email = request_data.email.strip()
    password = request_data.password.strip()

    # Check Admin credentials
    if email == "admin@campus.edu" and password == "admin123":
        access_token = create_access_token(data={"sub": email, "role": "admin"})
        return {"access_token": access_token, "token_type": "bearer", "role": "admin", "stall_id": None}

    # Check Vendor credentials
    vendor = db.query(Vendor).filter(Vendor.email == email).first()
    if not vendor or not verify_password(password, vendor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": vendor.email, "role": "vendor", "stall_id": vendor.stall_id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "vendor",
        "stall_id": vendor.stall_id
    }
