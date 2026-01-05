# P2H System - Backend API

Backend REST API untuk sistem **P2H (Pelaksanaan Pemeriksaan Harian)** kendaraan PT. IMM Bontang.

## 🚀 Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT (JSON Web Token)
- **Scheduler**: APScheduler
- **Notifications**: Telegram Bot API
- **Excel Processing**: Pandas + OpenPyXL

## 📋 Features

- ✅ Multi-role authentication (Superadmin, Admin Monitor, Karyawan)
- ✅ Vehicle master data management
- ✅ Dynamic P2H forms (EV, LV, DC, BIS)
- ✅ Shift management (Shift: 3x/day, Non-shift: 1x/day)
- ✅ Automated Telegram notifications
- ✅ Excel import/export
- ✅ STNK/KIR expiry alerts
- ✅ Comprehensive API documentation (Swagger)

## 🛠️ Installation

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Telegram Bot Token (dari @BotFather)

### 2. Clone Repository

```bash
git clone <repository-url>
cd backend
```

### 3. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env  # Windows
# atau
cp .env.example .env    # Linux/Mac
```

Edit `.env` dan isi dengan konfigurasi Anda:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/p2h_db
SECRET_KEY=your-secret-key-change-this
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_CHAT_ID=your-chat-id
```

### 6. Create Database

```bash
# Menggunakan psql atau pgAdmin
createdb p2h_db
```

### 7. Run Database Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 🏃 Running the Application

### Development Mode

**Quick Start (Recommended):**
```bash
# Interactive menu with all options
.\dev.ps1
```

**Manual Start:**
```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server akan berjalan di: **http://localhost:8000**

## 📖 API Documentation

Setelah server berjalan, akses dokumentasi API:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔑 Default Credentials

Setelah seeding data, gunakan credentials berikut untuk testing:

```
Username: [akan dibuat otomatis dari nama + tanggal lahir]
Password: [akan dibuat otomatis dari nama + tanggal lahir]
```

Format: `[NamaDepan][DDMMYYYY]`

## 🔧 Telegram Bot Setup

1. Buat bot baru dengan @BotFather di Telegram
2. Copy bot token
3. Tambahkan bot ke group yang diinginkan
4. Dapatkan chat ID group
5. Masukkan token dan chat ID ke `.env`

### Cara Mendapatkan Chat ID:

1. Tambahkan bot ke group
2. Kirim message di group
3. Akses: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Cari `"chat":{"id": -123456789}`

## 📅 Scheduled Jobs

Sistem akan otomatis menjalankan:

- **05:00 WITA**: Reset P2H tracker harian
- **05:00 WITA**: Cek expiry STNK/KIR (30 hari sebelum)
- **Setiap jam**: Retry failed Telegram notifications

## 📁 Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── utils/            # Helper functions
│   ├── scheduler/        # Background jobs
│   ├── config.py         # Settings
│   ├── database.py       # DB connection
│   └── main.py           # FastAPI app
├── docs/                 # Excel templates
├── scripts/              # Utility scripts
├── requirements.txt
└── .env
```

## 🧪 Testing

```bash
# TODO: Add tests
pytest tests/ -v
```

## 📝 Development Workflow

1. **Parse Excel Forms**: Run `scripts/parse_excel.py` untuk extract checklist items
2. **Seed Data**: Run `scripts/seed_data.py` untuk initial data
3. **Test API**: Gunakan Swagger UI untuk testing endpoints
4. **Check Logs**: Monitor console untuk scheduler jobs dan notifications

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL service
# Windows: services.msc -> PostgreSQL
# Linux: sudo systemctl status postgresql
```

### Migration Error

```bash
# Reset migrations
alembic downgrade base
alembic upgrade head
```

### Telegram Bot Not Sending

- Verify bot token di `.env`
- Check chat ID correct
- Ensure bot added to group/chat
- Check firewall/network settings

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 👥 Contributors

Tim Backend PT. IMM P2H System

## 📄 License

Internal use only - PT. IMM Bontang
