# Library Management System (Flask + SQLite)

This is a beginner-friendly web version of the Library Management System.

## Features
- Admin login (username: `admin`, password: `admin123`)
- Book management (add, view, search, delete)
- Student management (add, view, delete)
- Issue book
- Return book (quantity updates automatically)

## Local Run
1. Open terminal in this folder.
2. Create virtual environment (optional):
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Start app:
   - `python app.py`
5. Open browser:
   - `http://127.0.0.1:5000`

## Render Deployment
This project includes `render.yaml` for blueprint deploy.

### Steps
1. Push this project to GitHub.
2. In Render, create new Blueprint and select your repo.
3. Render reads `render.yaml` automatically.
4. After deploy, open the provided URL.

### Important for SQLite persistence on Render
- `render.yaml` mounts a disk at `/data`.
- `DB_PATH` is set to `/data/library.db`.
- Your data remains after restart/redeploy.

## Default Login
- Username: `admin`
- Password: `admin123`
