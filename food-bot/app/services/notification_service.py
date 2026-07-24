import os
import httpx
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

def safe_print(message_text: str):
    try:
        print(message_text)
    except UnicodeEncodeError:
        print(message_text.encode('ascii', 'ignore').decode())

def send_whatsapp_message(to_phone: str, message_text: str) -> dict:
    """
    Sends a plain text message to a user's WhatsApp number.
    """
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_API_TOKEN == "your_whatsapp_access_token_here":
        safe_print(f"[Simulated WhatsApp Text to {to_phone}]: {message_text}")
        return {"status": "simulated", "to": to_phone, "text": message_text}

    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=10.0)
            return response.json()
    except Exception as e:
        safe_print(f"Error sending WhatsApp message: {e}")
        return {"error": str(e)}

def send_whatsapp_button_message(to_phone: str, body_text: str, buttons: list) -> dict:
    """
    Sends an Interactive Button Message to a WhatsApp user.
    buttons = [ {"id": "btn_1", "title": "Pre-Book Food"}, {"id": "btn_2", "title": "Track Order"} ]
    """
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_API_TOKEN == "your_whatsapp_access_token_here":
        safe_print(f"[Simulated WhatsApp Buttons to {to_phone}]: {body_text} | Buttons: {[b['title'] for b in buttons]}")
        return {"status": "simulated", "to": to_phone, "buttons": buttons}

    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    formatted_buttons = [
        {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
        for b in buttons[:3]  # WhatsApp Cloud API supports max 3 quick reply buttons
    ]
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {"buttons": formatted_buttons}
        }
    }

    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload, timeout=10.0)
            return response.json()
    except Exception as e:
        safe_print(f"Error sending WhatsApp button message: {e}")
        return {"error": str(e)}
