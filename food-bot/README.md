# 🍕 Campus Flavored — WhatsApp Food Bot & Vendor/Admin Portal

An enterprise-grade, campus-wide food pre-booking platform featuring an interactive **WhatsApp Webhook Bot**, real-time **Vendor Operations Portal**, **Admin Analytics Dashboard**, and automated **Background Job Scheduler**.

---

## 🌟 Architecture Overview

```
                 +---------------------------------+
                 |  Student Mobile (WhatsApp Meta) |
                 +---------------------------------+
                                  |
                                  v  HTTP Webhook / POST /webhook
                 +---------------------------------+
                 |    FastAPI Python Backend       |
                 |  (StateMachine + Auth + APIs)   |
                 +---------------------------------+
                   /              |              \
                  /               |               \
                 v                v                v
     +-------------------+ +-------------+ +------------------+
     | React Vite Portal | |  PostgreSQL | | APScheduler Jobs |
     | (Vendor & Admin)  | |  / SQLite   | | (Auto-Complete  |
     +-------------------+ +-------------+ |  & Reminders)   |
                                           +------------------+
```

---

## 🚀 Key Features

### 📱 1. Student WhatsApp Experience
- **Interactive Ordering**: Browse open stalls, select portion sizes (`Full` / `Half`), accumulate cart, and reserve capacity-capped pickup slots.
- **Order Code Generation**: Unique tracking code (`ORD-XXXX`) generated upon checkout.
- **Order Tracking & History**: View active preparing status or past order history anytime.
- **Post-Pickup Rating Flow**: Automated completion trigger prompts 1-to-5 star order & item ratings directly via WhatsApp text.

### 👨‍🍳 2. Vendor Operations Dashboard
- **Live Order Queue**: Real-time order stream with 5-second auto-polling and status transition controls (`PREPARING`, `READY`, `COMPLETED`).
- **Menu Item CRUD**: Instant price updates, half-portion pricing toggle, and out-of-stock availability switch.
- **Stall Status Toggle**: Open/Close stall status that instantly updates student options in WhatsApp.
- **Stall Ratings & Sales**: Customer reviews and revenue analytics.

### 👑 3. Admin Control Center
- **All Stalls Overview**: Live operational status, order counts, and total revenue across all campus food vendors.
- **Sales Analytics**: Filterable revenue reports by date range and stall.
- **Low-Rating Alerts**: Automatic flagging of order and item ratings below 3.0 stars.
- **Vendor Provisioning**: Admin interface to create new vendor login accounts.

### ⏰ 4. Background Job Scheduler
- **Pickup Reminders**: Automated WhatsApp notifications ~15 minutes before scheduled pickup.
- **Order Auto-Completion**: Automatically marks pickup-expired orders as `COMPLETED` and dispatches WhatsApp rating prompts.

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11), Uvicorn, SQLAlchemy, Pydantic, Passlib (`pbkdf2_sha256`), python-jose (JWT), APScheduler.
- **Database**: PostgreSQL (Production) / SQLite (Development fallback).
- **Frontend**: React 18, Vite, Custom CSS (Glassmorphism dark theme).
- **Integrations**: Meta WhatsApp Cloud API Webhooks, ngrok.

---

## 🔑 Pre-Configured Demo Credentials

| Role | Email Address | Password | Stall / Scope |
| :--- | :--- | :--- | :--- |
| **Vendor Manager** | `basant@campus.edu` | `vendor123` | Basant Ice Cream (Stall #3) |
| **Vendor Manager** | `diner@campus.edu` | `vendor123` | Campus Diner (Stall #1) |
| **Vendor Manager** | `taco@campus.edu` | `vendor123` | Taco & Wrap Corner (Stall #2) |
| **System Admin** | `admin@campus.edu` | `admin123` | Global Access (All Stalls) |

- **WhatsApp Webhook Verify Token**: `campusflavored123`

---

## ⚡ Quickstart & Local Setup Guide

### 1. Start the backend locally

From the project root:

```powershell
cd food-bot
..\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend will create the SQLite database automatically on first start, seed demo data, and expose the API docs at http://127.0.0.1:8000/docs.

### Demo credentials

- Vendor: vendor@campus.edu / vendor123
- Admin: admin@campus.edu / admin123

### 2. Clone & Set Up Backend

```bash
cd food-bot

# Activate virtual environment
..\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Seed Database with Stalls, Menu Items, Vendors & Sample Ratings
python -m app.seed

# Run FastAPI Server
uvicorn app.main:app --reload --port 8000
```

Backend will be active at: `http://localhost:8000` (API Docs at `http://localhost:8000/docs`).

### 2. Set Up React Frontend Dashboard

```bash
cd food-bot/frontend

# Install dependencies
npm install

# Run Vite Dev Server
npm run dev
```

Frontend Dashboard active at: `http://localhost:3000`

---

## 🌐 Meta WhatsApp Webhook Integration

1. Start ngrok tunnel:
   ```bash
   ngrok http 8000
   ```
2. Copy public HTTPS ngrok URL (e.g. `https://unritual-superarctic-abram.ngrok-free.dev`).
3. In Meta Developer Console (WhatsApp Product $\rightarrow$ Configuration):
   - **Callback URL**: `https://unritual-superarctic-abram.ngrok-free.dev/webhook`
   - **Verify Token**: `campusflavored123`
4. Send messages from registered test numbers to interact with the bot!

---

## 🐳 Production Deployment

### Backend (Render / Docker)
- Deploy using provided `Dockerfile` or `render.yaml`.
- Environment Variables required:
  - `WHATSAPP_VERIFY_TOKEN`: `campusflavored123`
  - `JWT_SECRET`: `super_secret_jwt_key_campusflavored_2026`

### Frontend (Vercel / Netlify)
- Root Directory: `frontend`
- Build Command: `npm run build`
- Output Directory: `dist`
- Configured SPA redirects in `frontend/vercel.json`.
