# P2H System - Quick Reference Guide

## 🚀 Quick Start (First Time Setup)

### Method 1: Interactive Menu (RECOMMENDED)
```powershell
# Simple launcher (located in root)
.\dev.ps1

# Or directly access the menu
.\.venv\Scripts\setup.ps1
```
Pilih option 7 untuk complete setup!

### Method 2: Manual Commands
```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies (jika belum)
python -m pip install -r requirements.txt

# 3. Setup database
python -m alembic revision --autogenerate -m "Initial schema"
python -m alembic upgrade head

# 4. Seed data
python scripts/seed_data.py

# 5. Parse checklist (customize first!)
python scripts/parse_excel.py

# 6. Start server
python -m uvicorn app.main:app --reload
```

---

## ⚡ Quick Commands (After Setup)

### Activate Virtual Environment
```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1

# OR using helper script
.\.venv\Scripts\activate.ps1

# CMD/Batch
.\.venv\Scripts\activate.bat
```

### Start Development Server
```powershell
# PowerShell
.\.venv\Scripts\start_server.ps1

# CMD/Batch
.\.venv\Scripts\start_server.bat

# Manual
python -m uvicorn app.main:app --reload
```

### Database Migrations
```powershell
# Create migration
python -m alembic revision --autogenerate -m "Description"

# Apply migrations
python -m alembic upgrade head

# Rollback
python -m alembic downgrade -1
```

### Seed/Reset Data
```powershell
# Seed initial data
python scripts/seed_data.py

# Parse checklist from Excel
python scripts/parse_excel.py
```

---

## 📂 Helper Scripts Overview

**All helper scripts are now organized in `.venv\Scripts\` for a clean workspace!**

| Script | Location | Description | Usage |
|--------|----------|-------------|-------|
| `dev.ps1` | **Root** | **Quick launcher (RECOMMENDED)** | `.\dev.ps1` |
| `setup.ps1` | `.venv\Scripts\` | Interactive setup menu | `.\.venv\Scripts\setup.ps1` |
| `setup_database.ps1` | `.venv\Scripts\` | Database setup wizard | `.\.venv\Scripts\setup_database.ps1` |
| `activate.ps1` | `.venv\Scripts\` | Activate venv (PowerShell) | `.\.venv\Scripts\activate.ps1` |
| `activate.bat` | `.venv\Scripts\` | Activate venv (CMD) | `.\.venv\Scripts\activate.bat` |
| `start_server.ps1` | `.venv\Scripts\` | Start server (PowerShell) | `.\.venv\Scripts\start_server.ps1` |
| `start_server.bat` | `.venv\Scripts\` | Start server (CMD) | `.\.venv\Scripts\start_server.bat` |

**TIP:** Just run `.\dev.ps1` from root directory for quick access to all tools!

---

## 🔑 Default Credentials

After running `seed_data.py`:

**Superadmin:**
- Username: `Admin01011990`
- Password: `Admin01011990`

**Admin Monitor:**
- Username: `Monitor15051992`
- Password: `Monitor15051992`

**Karyawan:**
- Username: `Budi20061995` / Password: `Budi20061995`
- Username: `Andi10031993` / Password: `Andi10031993`

---

## 🌐 API Endpoints

Server running at: **http://localhost:8000**

- 📚 **Swagger UI**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc
- 🔍 **Health Check**: http://localhost:8000/health

---

## 🛠️ Common Tasks

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Admin01011990","password":"Admin01011990"}'
```

### Test Barcode Scan
```bash
curl http://localhost:8000/vehicles/lambung/EV001 \
  -H "Authorization: Bearer <token>"
```

### Test P2H Submission
1. Get token from login
2. Get vehicle by barcode scan
3. Get checklist: `GET /p2h/checklist/EV`
4. Submit P2H: `POST /p2h/submit`

---

## 📝 Notes

- Virtual environment must be activated before running any Python commands
- Check `.env` file for proper configuration
- PostgreSQL must be running for database operations
- Telegram bot token required for notifications

---

## 🆘 Troubleshooting

**Script execution policy error?**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port 8000 already in use?**
```powershell
# Use different port
python -m uvicorn app.main:app --reload --port 8001
```

**Database connection error?**
- Check PostgreSQL is running
- Verify `.env` DATABASE_URL
- Test connection: `psql -U postgres -d p2h_db`
