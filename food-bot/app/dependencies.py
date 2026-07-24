from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import Vendor
from .auth_utils import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_email: str = payload.get("sub")
    role: str = payload.get("role")
    if user_email is None or role is None:
        raise credentials_exception

    if role == "vendor":
        vendor = db.query(Vendor).filter(Vendor.email == user_email).first()
        if vendor is None:
            raise credentials_exception
        return {"user": vendor, "role": role, "stall_id": vendor.stall_id}
    elif role == "admin":
        return {"user": user_email, "role": "admin", "stall_id": None}
    else:
        raise credentials_exception

def get_current_vendor(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Vendor role required"
        )
    return current_user

def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin role required"
        )
    return current_user
