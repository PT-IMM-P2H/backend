# 🚀 Cara Menjalankan Backend P2H

Panduan cepat untuk menjalankan backend sistem P2H.

---

## 📌 Setup Awal (Hanya Sekali)

### 1. Buat Virtual Environment
```powershell
python -m venv .venv
```

### 2. Aktifkan Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Buat File `.env`
Buat file `.env` di folder `backend/` dengan isi:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/p2h_db

# JWT Secret (generate random string)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram Bot
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
TELEGRAM_CHAT_ID=your-chat-id

# Environment
ENVIRONMENT=development
```

### 5. Setup Database
```powershell
# Jalankan migrasi
alembic upgrade head

# Seed data awal (users, checklist, dll)
python -m app.seeds.seed_data
```

---

## ▶️ Cara Jalankan Sehari-hari

### 1. Aktifkan Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*Catatan: Pastikan terminal Anda menunjukkan `(.venv)` di awal baris*

### 2. Jalankan Server
```powershell
uvicorn app.main:app --reload
```

atau dengan host dan port spesifik:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Akses Aplikasi
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

---

## 🔧 Perintah Berguna

### Database

#### Membuat Migration Baru
```powershell
alembic revision --autogenerate -m "deskripsi perubahan"
```

#### Jalankan Migration
```powershell
alembic upgrade head
```

#### Rollback Migration
```powershell
alembic downgrade -1
```

#### Cek Status Migration
```powershell
alembic current
alembic history
```

### Seed Data

#### Seed Users
```powershell
python -m app.seeds.seed_users
```

#### Seed Checklist
```powershell
python -m app.seeds.seed_checklist
```

#### Seed Semua Data
```powershell
python -m app.seeds.seed_data
```

### Development

#### Install Package Baru
```powershell
pip install nama-package
pip freeze > requirements.txt
```

#### Cek Versi Python
```powershell
python --version
```

#### Deaktivasi Virtual Environment
```powershell
deactivate
```

---

## 🐛 Troubleshooting

### Error: "alembic: command not found"
**Solusi**: Pastikan virtual environment sudah aktif
```powershell
.\.venv\Scripts\Activate.ps1
```

### Error: "No module named 'app'"
**Solusi**: Pastikan menjalankan perintah dari folder `backend/`
```powershell
cd backend
```

### Error: Database Connection
**Solusi**: 
1. Cek PostgreSQL sudah running
2. Cek kredensial di file `.env`
3. Cek database sudah dibuat: `CREATE DATABASE p2h_db;`

### Error: Port sudah digunakan
**Solusi**: Gunakan port lain
```powershell
uvicorn app.main:app --port 8001 --reload
```

---

## 👤 Default Login

Setelah seed data, gunakan kredensial ini untuk login:

**Superadmin**
- Email: `superadmin@imm.com`
- Password: `admin123`

**Admin Monitor**
- Email: `admin@imm.com`
- Password: `admin123`

**Karyawan**
- Email: `karyawan@imm.com`
- Password: `admin123`

---

## 📁 Struktur Project Penting

```
backend/
├── app/
│   ├── main.py              # Entry point aplikasi
│   ├── config.py            # Konfigurasi
│   ├── database.py          # Database connection
│   ├── dependencies.py      # Dependency injection
│   ├── models/              # SQLAlchemy models
│   ├── routers/             # API routes
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Helper functions
├── alembic/                 # Database migrations
├── .env                     # Environment variables (BUAT MANUAL)
└── requirements.txt         # Python dependencies
```

---

## 🔄 Workflow Harian

1. **Buka Terminal** di folder `backend/`
2. **Aktifkan venv**: `.\.venv\Scripts\Activate.ps1`
3. **Jalankan server**: `uvicorn app.main:app --reload`
4. **Develop**: Edit code, server auto-reload
5. **Test**: Buka http://localhost:8000/docs
6. **Commit**: Git add, commit, push
7. **Selesai**: Ctrl+C untuk stop server, `deactivate` untuk keluar venv

---

## 📞 Bantuan Lebih Lanjut

- Dokumentasi FastAPI: https://fastapi.tiangolo.com
- Dokumentasi Alembic: https://alembic.sqlalchemy.org
- Dokumentasi SQLAlchemy: https://docs.sqlalchemy.org

---

**Terakhir diupdate**: 8 Januari 2026
