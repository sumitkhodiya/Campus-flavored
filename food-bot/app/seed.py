import os
import re
import pandas as pd
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import Stall, Vendor, MenuItem, Slot, Student, Order, OrderItem, OrderRating, ItemRating
from .auth_utils import get_password_hash

EXCEL_FILE_PATH = r"C:\Users\sumit\Downloads\Project2_merged_data.xlsx"

def reset_and_seed_database(db: Session):
    print("=== REMOVING ALL PREVIOUS DATA & RE-CREATING TABLES ===")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables reset successfully.")

    print(f"\n=== READING DATASET FROM: {EXCEL_FILE_PATH} ===")
    if not os.path.exists(EXCEL_FILE_PATH):
        raise FileNotFoundError(f"Excel dataset file not found at: {EXCEL_FILE_PATH}")

    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='Sheet1')
    print(f"Loaded {len(df)} total rows from Excel dataset.")

    # Clean string columns
    df['Restaurant'] = df['Restaurant'].astype(str).str.strip()
    df['Area'] = df['Area'].fillna('').astype(str).str.strip()
    df['Block'] = df['Block'].fillna('').astype(str).str.strip()
    df['Category'] = df['Category'].fillna('').astype(str).str.strip()
    df['Item'] = df['Item'].fillna('').astype(str).str.strip()
    df['Variant'] = df['Variant'].fillna('').astype(str).str.strip()
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)

    # 1. Create Unique Stalls
    unique_stalls_df = df[['Restaurant', 'Area', 'Block']].drop_duplicates().reset_index(drop=True)
    print(f"Found {len(unique_stalls_df)} unique stalls in dataset.")

    stall_map = {}
    stalls_list = []
    vendors_list = []

    time_slot_templates = [
        "11:00 AM - 11:30 AM",
        "11:30 AM - 12:00 PM",
        "12:00 PM - 12:30 PM",
        "12:30 PM - 01:00 PM",
        "01:00 PM - 01:30 PM",
        "01:30 PM - 02:00 PM",
        "02:00 PM - 02:30 PM",
        "02:30 PM - 03:00 PM",
        "06:00 PM - 06:30 PM",
        "06:30 PM - 07:00 PM",
        "07:00 PM - 07:30 PM",
        "07:30 PM - 08:00 PM",
    ]

    for idx, row in unique_stalls_df.iterrows():
        rest_name = row['Restaurant']
        area = row['Area']
        block = row['Block']
        location = f"{area}, {block}" if (area and block) else (area or block or "Campus Food Court")

        stall = Stall(name=rest_name, location=location, is_open=True)
        db.add(stall)
        db.commit()
        db.refresh(stall)
        stall_map[rest_name] = stall

        # Create Vendor Account per Stall
        slug = re.sub(r'[^a-zA-Z0-9]', '_', rest_name.lower()).strip('_')
        email = f"{slug}_{idx+1}@campus.edu"
        
        vendor = Vendor(
            name=f"{rest_name} Manager",
            email=email,
            hashed_password=get_password_hash("vendor123"),
            stall_id=stall.id
        )
        vendors_list.append(vendor)

        # Create Pickup Time Slots per Stall
        for slot_time in time_slot_templates:
            slot = Slot(stall_id=stall.id, time=slot_time, capacity=10)
            db.add(slot)

    db.add_all(vendors_list)

    # Alias Demo Vendors for easy testing
    if "Basant Icecream" in stall_map:
        basant_stall = stall_map["Basant Icecream"]
        db.add(Vendor(name="Basant Manager", email="basant@campus.edu", hashed_password=get_password_hash("vendor123"), stall_id=basant_stall.id))

    if "LovelyBakeStudio" in stall_map:
        diner_stall = stall_map["LovelyBakeStudio"]
        db.add(Vendor(name="Diner Manager", email="diner@campus.edu", hashed_password=get_password_hash("vendor123"), stall_id=diner_stall.id))

    # Add System Admin Account
    admin_vendor = Vendor(name="Campus Admin", email="admin@campus.edu", hashed_password=get_password_hash("admin123"), stall_id=None)
    db.add(admin_vendor)

    db.commit()
    print(f"Created {len(unique_stalls_df)} Stalls & Vendors in Database.")

    # 2. Insert All Menu Items
    menu_items_list = []
    for _, row in df.iterrows():
        rest_name = row['Restaurant']
        if rest_name not in stall_map:
            continue

        stall = stall_map[rest_name]
        item_name = row['Item']
        variant = row['Variant']
        price = float(row['Price'])

        if variant and variant.lower() != 'nan' and variant.strip() != '':
            full_name = f"{item_name} ({variant})"
        else:
            full_name = item_name

        half_price = None
        if variant and variant.lower() == 'half':
            half_price = price

        menu_item = MenuItem(
            stall_id=stall.id,
            name=full_name,
            price=price,
            half_price=half_price,
            available=True
        )
        menu_items_list.append(menu_item)

    db.add_all(menu_items_list)
    db.commit()
    print(f"Inserted {len(menu_items_list)} Menu Items into Database.")

    # 3. Seed Sample Student & Order for Live Demo Readiness
    demo_student = Student(reg_number="2023CS099", name="Rahul Sharma", phone_number="+919876543210")
    db.add(demo_student)
    db.commit()
    db.refresh(demo_student)

    # Find an item from Basant Icecream
    basant_item = db.query(MenuItem).filter(MenuItem.stall_id == stall_map["Basant Icecream"].id).first()
    
    if basant_item:
        demo_order = Order(
            student_id=demo_student.reg_number,
            order_code="ORD-8821",
            status="COMPLETED",
            pickup_time="01:30 PM - 02:00 PM"
        )
        db.add(demo_order)
        db.commit()
        db.refresh(demo_order)

        demo_order_item = OrderItem(
            order_id=demo_order.id,
            menu_item_id=basant_item.id,
            quantity=2,
            portion="FULL"
        )
        db.add(demo_order_item)

        demo_order_rating = OrderRating(order_id=demo_order.id, rating=5, review="Super fast pickup and fresh food!")
        demo_item_rating = ItemRating(menu_item_id=basant_item.id, student_id=demo_student.reg_number, rating=5, review="Delicious!")
        db.add_all([demo_order_rating, demo_item_rating])
        db.commit()

    print("\n[SUCCESS] DATABASE RESET & RE-SEEDED SUCCESSFULLY FROM EXCEL DATASET!")

def query_summary(db: Session):
    total_stalls = db.query(Stall).count()
    total_vendors = db.query(Vendor).count()
    total_items = db.query(MenuItem).count()
    total_slots = db.query(Slot).count()

    print(f"\n--- DATABASE SUMMARY ---")
    print(f"Total Stalls: {total_stalls}")
    print(f"Total Vendors: {total_vendors}")
    print(f"Total Menu Items: {total_items}")
    print(f"Total Pickup Time Slots: {total_slots}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        reset_and_seed_database(db)
        query_summary(db)
    finally:
        db.close()
