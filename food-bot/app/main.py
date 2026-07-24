from fastapi import FastAPI, Request, Query, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
import os
from .database import get_db, initialize_database
from .state_machine import StateMachine
from .services.notification_service import send_whatsapp_message
from .services.scheduler import start_scheduler
from .routers.auth import router as auth_router
from .routers.vendor import router as vendor_router
from .routers.ratings import router as ratings_router
from .routers.admin import router as admin_router

app = FastAPI(
    title="Food Bot API",
    description="Campus Flavored WhatsApp Food Bot & Background Jobs API",
    version="1.0.0"
)

# Initialize Background Job Scheduler on Startup
@app.on_event("startup")
def startup_event():
    try:
        initialize_database()
    except Exception as e:
        print(f"Database initialization warning: {e}")

    try:
        start_scheduler()
    except Exception as e:
        print(f"Scheduler startup warning: {e}")

# Register Routers
app.include_router(auth_router)
app.include_router(vendor_router)
app.include_router(ratings_router)
app.include_router(admin_router)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "campusflavored123")

@app.get("/")
def read_root():
    return {"message": "Welcome to Food Bot API! Webhook active at /webhook", "docs": "/docs"}

@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)
    return PlainTextResponse(content="Verification failed", status_code=403)

@app.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    try:
        if "entry" in body:
            for entry in body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    for msg in messages:
                        from_phone = msg.get("from")
                        msg_type = msg.get("type")
                        incoming_text = ""

                        if msg_type == "text":
                            incoming_text = msg.get("text", {}).get("body", "")
                        elif msg_type == "interactive":
                            interactive = msg.get("interactive", {})
                            if "button_reply" in interactive:
                                incoming_text = interactive["button_reply"].get("id", "")
                            elif "list_reply" in interactive:
                                incoming_text = interactive["list_reply"].get("id", "")

                        if from_phone and incoming_text:
                            reply_text = StateMachine.process_message(db, from_phone, incoming_text)
                            send_whatsapp_message(from_phone, reply_text)
    except Exception as e:
        print(f"Error processing webhook payload: {e}")

    return {"status": "received"}
