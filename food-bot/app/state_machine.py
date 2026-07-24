from sqlalchemy.orm import Session
from .models import Student, Stall, MenuItem, Order
from .services.menu_service import MenuService
from .services.order_service import OrderService
from .services.slot_service import SlotService
from .services.rating_service import RatingService
from .services.notification_service import send_whatsapp_message, send_whatsapp_button_message

USER_SESSIONS = {}

def get_user_session(phone_number: str) -> dict:
    if phone_number not in USER_SESSIONS:
        USER_SESSIONS[phone_number] = {
            "state": "MAIN_MENU",
            "selected_stall_id": None,
            "cart": [],
            "selected_slot_id": None,
            "selected_slot_time": None,
            "rating_order_id": None,
            "rating_items_list": [],
            "rating_item_index": 0
        }
    return USER_SESSIONS[phone_number]

def clear_user_session(phone_number: str):
    USER_SESSIONS[phone_number] = {
        "state": "MAIN_MENU",
        "selected_stall_id": None,
        "cart": [],
        "selected_slot_id": None,
        "selected_slot_time": None,
        "rating_order_id": None,
        "rating_items_list": [],
        "rating_item_index": 0
    }

class StateMachine:
    @staticmethod
    def process_message(db: Session, phone_number: str, message_text: str) -> str:
        student = db.query(Student).filter(Student.phone_number == phone_number).first()
        if not student:
            student = Student(reg_number=f"REG-{phone_number[-6:]}", name=f"Student {phone_number[-4:]}", phone_number=phone_number)
            db.add(student)
            db.commit()
            db.refresh(student)

        session = get_user_session(phone_number)
        current_state = session["state"]
        input_clean = message_text.strip().lower()

        if input_clean in ["hi", "hello", "menu", "start", "restart", "0"]:
            clear_user_session(phone_number)
            session = get_user_session(phone_number)
            current_state = "MAIN_MENU"

        response = ""

        # Trigger Rating Flow
        if input_clean in ["rate", "rating", "5", "feedback"]:
            completed_orders = db.query(Order).filter(
                Order.student_id == student.reg_number,
                Order.status == "COMPLETED"
            ).order_by(Order.created_at.desc()).all()

            if not completed_orders:
                response = "You don't have any completed orders eligible for rating yet."
            else:
                last_completed = completed_orders[0]
                session["rating_order_id"] = last_completed.id
                session["rating_items_list"] = [oi.menu_item for oi in last_completed.items]
                session["rating_item_index"] = 0
                session["state"] = "RATING_ORDER"
                
                return (
                    f"⭐ *Rate Your Order ({last_completed.order_code})*\n\n"
                    "How was your overall experience (1 to 5 Stars)?\n"
                    "Reply with a number from 1 (poor) to 5 (excellent) plus an optional review!\n"
                    "*(Example: '5 Fast delivery & hot food!')*"
                )

        # -------------------------------------------------------------
        # STATE: RATING_ORDER
        # -------------------------------------------------------------
        if current_state == "RATING_ORDER":
            order_id = session["rating_order_id"]
            rating_num = None
            review_text = ""

            # Extract integer rating 1-5
            words = input_clean.split()
            for word in words:
                if word.isdigit():
                    val = int(word)
                    if 1 <= val <= 5:
                        rating_num = val
                        break

            if rating_num is not None:
                review_text = message_text.replace(str(rating_num), "").strip()
                RatingService.submit_order_rating(db, order_id, rating_num, review_text)

                items = session["rating_items_list"]
                if items:
                    session["state"] = "RATING_ITEMS"
                    session["rating_item_index"] = 0
                    first_item = items[0]
                    response = (
                        f"Thank you for rating your overall order! ⭐ ({rating_num}/5)\n\n"
                        f"Now please rate item 1 of {len(items)}:\n"
                        f"🔹 *{first_item.name}* (1 to 5 Stars)\n"
                        "*(Example: '5 Tasted delicious!')*"
                    )
                else:
                    clear_user_session(phone_number)
                    response = "Thank you for your rating & feedback! 🎉"
            else:
                response = "Please reply with a valid rating number between 1 and 5 (e.g. '5 Great food!')."

        # -------------------------------------------------------------
        # STATE: RATING_ITEMS
        # -------------------------------------------------------------
        elif current_state == "RATING_ITEMS":
            items = session["rating_items_list"]
            idx = session["rating_item_index"]

            rating_num = None
            for word in input_clean.split():
                if word.isdigit():
                    val = int(word)
                    if 1 <= val <= 5:
                        rating_num = val
                        break

            if rating_num is not None:
                current_item = items[idx]
                review_text = message_text.replace(str(rating_num), "").strip()
                RatingService.submit_item_rating(db, current_item.id, student.reg_number, rating_num, review_text)

                session["rating_item_index"] += 1
                next_idx = session["rating_item_index"]

                if next_idx < len(items):
                    next_item = items[next_idx]
                    response = (
                        f"Saved {rating_num}/5 rating for *{current_item.name}*! ⭐\n\n"
                        f"Now rate item {next_idx + 1} of {len(items)}:\n"
                        f"🔹 *{next_item.name}* (1 to 5 Stars)"
                    )
                else:
                    clear_user_session(phone_number)
                    response = "🎉 *Thank you for rating all your items!* Your feedback helps improve campus food quality. ⭐\n\nReply '0' for Main Menu."
            else:
                response = "Please reply with a rating between 1 and 5 stars."

        # -------------------------------------------------------------
        # STATE: MAIN_MENU / IDLE
        # -------------------------------------------------------------
        elif current_state == "MAIN_MENU" or current_state == "IDLE":
            if input_clean in ["1", "prebook", "pre-book", "order", "view menu"]:
                open_stalls = db.query(Stall).filter(Stall.is_open == True).all()
                if not open_stalls:
                    response = "Sorry, all food stalls are currently closed. Please check back later! 🚪"
                else:
                    response = "📍 *Select a Food Stall to order from:*\n\n"
                    for stall in open_stalls:
                        response += f"🔹 *Reply '{stall.id}'* for *{stall.name}* ({stall.location})\n"
                    response += "\nReply with the Stall Number to view its menu."
                    session["state"] = "BROWSING_MENU"

            elif input_clean in ["2", "track", "track order"]:
                active_orders = OrderService.get_student_active_orders(db, student.reg_number)
                if not active_orders:
                    response = "You have no active orders right now. Reply '1' to place an order!"
                else:
                    response = "📦 *Your Active Orders:*\n\n"
                    for ord in active_orders:
                        response += f"• *{ord.order_code}* | Status: *{ord.status}* | Pickup: *{ord.pickup_time}*\n"
                        for item in ord.items:
                            response += f"   - {item.menu_item.name} ({item.portion}) x{item.quantity}\n"
                    response += "\nReply '0' for Main Menu."

            elif input_clean in ["3", "history", "order history"]:
                history = OrderService.get_student_order_history(db, student.reg_number)
                if not history:
                    response = "You haven't placed any past orders yet. Reply '1' to place your first order!"
                else:
                    response = "📜 *Your Order History:*\n\n"
                    for ord in history[:5]:
                        response += f"• *{ord.order_code}* | Status: {ord.status} | Date: {ord.created_at.strftime('%d %b %H:%M')}\n"
                    response += "\nReply 'rate' to rate your completed orders!"

            elif input_clean in ["4", "cancel", "cancel order"]:
                active_orders = OrderService.get_student_active_orders(db, student.reg_number)
                pending_orders = [o for o in active_orders if o.status in ["PENDING", "CONFIRMED"]]
                if not pending_orders:
                    response = "You have no pending orders eligible for cancellation."
                else:
                    response = "❌ *Select an order to cancel:*\n\n"
                    for o in pending_orders:
                        response += f"• Reply 'cancel {o.id}' to cancel Order *{o.order_code}*\n"
                
            elif input_clean.startswith("cancel "):
                try:
                    order_id_to_cancel = int(input_clean.split(" ")[1])
                    success = OrderService.cancel_order(db, order_id_to_cancel)
                    if success:
                        response = f"Order #{order_id_to_cancel} has been successfully CANCELLED. ❌"
                    else:
                        response = "Could not cancel order. It may already be preparing or completed."
                except Exception:
                    response = "Invalid cancel command format."

            else:
                response = (
                    "👋 *Welcome to Campus Flavored Food Bot!* 🍕🍔\n\n"
                    "What would you like to do today?\n\n"
                    "1️⃣ *Pre-Book Food* (View Menu & Order)\n"
                    "2️⃣ *Track Active Order*\n"
                    "3️⃣ *Order History*\n"
                    "4️⃣ *Cancel Pending Order*\n\n"
                    "Reply with *1*, *2*, *3*, or *4* to proceed."
                )

        # -------------------------------------------------------------
        # STATE: BROWSING_MENU
        # -------------------------------------------------------------
        elif current_state == "BROWSING_MENU":
            open_stalls = db.query(Stall).filter(Stall.is_open == True).all()
            selected_stall = None

            try:
                stall_id_choice = int(input_clean)
                selected_stall = next((s for s in open_stalls if s.id == stall_id_choice), None)
            except ValueError:
                for s in open_stalls:
                    if s.name.lower() in input_clean:
                        selected_stall = s
                        break

            if selected_stall:
                session["selected_stall_id"] = selected_stall.id
                items = MenuService.get_items_by_stall(db, selected_stall.id)

                if not items:
                    response = f"No items currently available at {selected_stall.name}. Reply '0' to return."
                else:
                    response = f"📋 *Menu for {selected_stall.name}:*\n\n"
                    for item in items[:20]:
                        half_info = f" (Half: Rs. {item.half_price:.2f})" if item.half_price else ""
                        response += f"• *{item.id}*. {item.name} - Full: Rs. {item.price:.2f}{half_info}\n"
                    
                    response += (
                        "\n🛒 *How to add items to cart:*\n"
                        "• Reply `add <Item ID>` (e.g., `add 1`)\n"
                        "• Reply `add <Item ID> half` for Half portion\n"
                        "• Reply `checkout` when done selecting items."
                    )
                    session["state"] = "SELECTING_ITEMS"
            else:
                response = "Invalid stall selection. Please reply with a valid Stall Number, or reply '0' for Main Menu."

        # -------------------------------------------------------------
        # STATE: SELECTING_ITEMS
        # -------------------------------------------------------------
        elif current_state == "SELECTING_ITEMS":
            stall_id = session["selected_stall_id"]

            if input_clean == "checkout" or input_clean == "done":
                if not session["cart"]:
                    response = "Your cart is empty! Please add at least one item using `add <Item ID>` before checkout."
                else:
                    available_slots = SlotService.get_slots_by_stall(db, stall_id)
                    if not available_slots:
                        response = "Sorry, there are no pickup slots remaining for this stall today."
                    else:
                        response = "⏰ *Select a Pickup Time Slot:*\n\n"
                        for slot in available_slots:
                            response += f"🔹 *Reply '{slot.id}'* for *{slot.time}* (Remaining Capacity: {slot.capacity})\n"
                        session["state"] = "SELECTING_TIME"

            elif input_clean.startswith("add "):
                parts = input_clean.split()
                try:
                    item_id = int(parts[1])
                    portion = "HALF" if len(parts) > 2 and parts[2] == "half" else "FULL"
                    
                    item = db.query(MenuItem).filter(MenuItem.id == item_id, MenuItem.stall_id == stall_id).first()
                    if not item:
                        response = f"Item #{item_id} not found in this stall's menu."
                    else:
                        if portion == "HALF" and not item.half_price:
                            portion = "FULL"
                            response = f"Half portion not available for {item.name}. Added Full portion instead.\n\n"
                        else:
                            response = ""

                        existing = next((c for c in session["cart"] if c["menu_item_id"] == item_id and c["portion"] == portion), None)
                        if existing:
                            existing["quantity"] += 1
                        else:
                            session["cart"].append({"menu_item_id": item_id, "quantity": 1, "portion": portion})

                        total = 0.0
                        cart_summary = ""
                        for c in session["cart"]:
                            m_item = db.query(MenuItem).get(c["menu_item_id"])
                            price = m_item.half_price if (c["portion"] == "HALF" and m_item.half_price) else m_item.price
                            subtotal = price * c["quantity"]
                            total += subtotal
                            cart_summary += f"   - {m_item.name} ({c['portion']}) x{c['quantity']} = Rs. {subtotal:.2f}\n"

                        response += (
                            f"✅ Added *{item.name} ({portion})* to cart!\n\n"
                            f"🛒 *Current Cart Summary:*\n{cart_summary}"
                            f"💰 *Total:* Rs. {total:.2f}\n\n"
                            "Reply `add <Item ID>` to add more, or `checkout` to choose pickup slot."
                        )
                except (IndexError, ValueError):
                    response = "Invalid format. Reply `add <Item ID>` (e.g. `add 1` or `add 1 half`)."
            else:
                response = "Reply `add <Item ID>` to add items to cart, or `checkout` to proceed."

        # -------------------------------------------------------------
        # STATE: SELECTING_TIME
        # -------------------------------------------------------------
        elif current_state == "SELECTING_TIME":
            stall_id = session["selected_stall_id"]
            available_slots = SlotService.get_slots_by_stall(db, stall_id)
            selected_slot = None

            try:
                slot_id_choice = int(input_clean)
                selected_slot = next((s for s in available_slots if s.id == slot_id_choice), None)
            except ValueError:
                pass

            if selected_slot:
                session["selected_slot_id"] = selected_slot.id
                session["selected_slot_time"] = selected_slot.time
                
                total = 0.0
                summary = f"📝 *ORDER SUMMARY*\n"
                summary += f"📍 Stall: *{selected_slot.stall.name}*\n"
                summary += f"⏰ Pickup Time: *{selected_slot.time}*\n\n"
                summary += "🛒 *Items:*\n"
                
                for c in session["cart"]:
                    m_item = db.query(MenuItem).get(c["menu_item_id"])
                    price = m_item.half_price if (c["portion"] == "HALF" and m_item.half_price) else m_item.price
                    subtotal = price * c["quantity"]
                    total += subtotal
                    summary += f"   • {m_item.name} ({c['portion']}) x{c['quantity']} - Rs. {subtotal:.2f}\n"

                summary += f"\n💰 *Total Amount:* Rs. {total:.2f}\n\n"
                summary += "Reply *'confirm'* to place this order, or *'cancel'* to start over."
                
                session["state"] = "CONFIRMED"
                response = summary
            else:
                response = "Invalid slot choice. Please reply with a valid Slot ID Number from the list above."

        # -------------------------------------------------------------
        # STATE: CONFIRMED
        # -------------------------------------------------------------
        elif current_state == "CONFIRMED":
            if input_clean == "confirm" or input_clean == "yes":
                slot_id = session["selected_slot_id"]
                pickup_time = session["selected_slot_time"]
                cart = session["cart"]

                success_reserve = SlotService.reserve_slot(db, slot_id)
                if not success_reserve:
                    response = "Sorry, that pickup slot just filled up! Please reply '1' to re-select a slot."
                    session["state"] = "MAIN_MENU"
                else:
                    order = OrderService.create_confirmed_order(
                        db=db,
                        student_id=student.reg_number,
                        items_draft=cart,
                        pickup_time=pickup_time
                    )
                    
                    order_total = OrderService.calculate_order_total(order)

                    response = (
                        f"🎉 *ORDER PLACED SUCCESSFULLY!*\n\n"
                        f"🆔 *Order Code:* `{order.order_code}`\n"
                        f"⏰ *Pickup Time:* {order.pickup_time}\n"
                        f"💰 *Total:* Rs. {order_total:.2f}\n"
                        f"📌 *Status:* {order.status}\n\n"
                        "Show your *Order Code* at the stall during pickup! 🍔\n"
                        "Reply '0' for Main Menu."
                    )

                    clear_user_session(phone_number)

            elif input_clean == "cancel" or input_clean == "no":
                clear_user_session(phone_number)
                response = "Order cancelled. Reply '1' whenever you'd like to order again!"
            else:
                response = "Please reply *'confirm'* to place your order or *'cancel'* to discard it."

        return response
