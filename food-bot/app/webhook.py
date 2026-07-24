from fastapi import APIRouter, Request, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from .database import get_db
from .state_machine import StateMachine

router = APIRouter(prefix="/webhook", tags=["Webhook"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "my_secure_verify_token_123")

@router.get("")
def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    challenge: int = Query(None, alias="hub.challenge"),
    verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Verification endpoint for WhatsApp Cloud API.
    """
    if mode and verify_token:
        if mode == "subscribe" and verify_token == VERIFY_TOKEN:
            print("Webhook Verified Successfully")
            return challenge
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing verification parameters")


@router.post("")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint that receives messages from WhatsApp.
    """
    payload = await request.json()
    print("Received webhook payload:", payload)

    try:
        if "entry" in payload:
            for entry in payload["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for msg in value["messages"]:
                            phone_number = msg.get("from")
                            msg_type = msg.get("type")
                            
                            if msg_type == "text" and "text" in msg:
                                message_text = msg["text"].get("body", "")
                                
                                # Process through State Machine
                                reply = StateMachine.process_message(db, phone_number, message_text)
                                print(f"Received from {phone_number}: '{message_text}' -> Reply: '{reply}'")
                                
                                # In production: send_whatsapp_message(phone_number, reply)
                                
    except Exception as e:
        print(f"Error parsing webhook payload: {e}")
        
    return {"status": "success"}
