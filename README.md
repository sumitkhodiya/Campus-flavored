# Campus Flavored — Vendor & Admin Portal

This repository contains the Campus Flavored vendor and admin portal: a FastAPI backend (food-bot) and a React (Vite) frontend for managing campus food stalls, orders, ratings, and sales.

## Project Structure

- `food-bot/` — FastAPI backend (app, services, routers)
	- `app/` — application code (main, routers, services, database utils)
	- `requirements.txt` — backend Python dependencies
- `frontend/` — React + Vite frontend (Vendor/Admin dashboards)

## Prerequisites

- Python 3.10+ (3.12 tested locally)
- Node.js 16+ and npm
- Git and a working GitHub account (for pushing)

## Backend — Run locally

Windows (PowerShell):

```powershell
cd food-bot
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
# initialize DB (tables & seed) happens automatically on startup
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open API docs at: http://127.0.0.1:8000/docs

Demo credentials (seeded locally):
- Vendor: `basant@campus.edu` / `vendor123`
- Admin: `admin@campus.edu` / `admin123`

## Frontend — Run locally

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
# open http://localhost:3000
```

## Notes

- The backend uses SQLite by default if PostgreSQL is not configured.
- The scheduler and background jobs are started on app startup.
- WhatsApp/notification integration is simulated unless real credentials are provided.

## Pushing to GitHub

To push this repository to GitHub (already configured remote URL):

```bash
git add .
git commit -m "Add README and professional icons, update frontend theme"
git branch -M main
git remote add origin https://github.com/sumitkhodiya/Campus-flavored.git
git push -u origin main
```

If you already have a remote named `origin`, use `git remote set-url origin <url>` instead.

---
If you'd like, I can push these changes now from this environment (it will use your local git credentials). Proceed? 

