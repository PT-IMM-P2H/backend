import sys
from pathlib import Path
from sqlalchemy.orm import Session

# 1. Tambahkan root directory ke sys.path (Konsisten dengan seed_data.py Anda)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import SessionLocal
from app.models.checklist import ChecklistTemplate

def seed_p2h_checklists(db: Session):
    print("📋 Seeding 39 Item Checklist Templates (Multi-Tagging)...")
    
    # Definisi Tags (Sesuai dengan modal UI yang Anda kirim)
    all_vehicles = [
        "Light Vehicle", "Electric Vehicle", "Double Cabin", "Single Cabin", 
        "Bus", "Ambulance", "Fire Truck", "Komando", "Truk Sampah"
    ]
    
    all_shifts = ["Long Shift", "No Shift", "Shift 1", "Shift 2", "Shift 3"]
    default_options = ["Normal", "Abnormal", "Warning"]

    # List 39 Pertanyaan berdasarkan data Anda
    items_to_seed = [
        # SECTION: OLI & RADIATOR
        {"section": "OLI & RADIATOR", "item": "OLI MESIN: Volume oli normal & tidak bocor?", "order": 1},
        {"section": "OLI & RADIATOR", "item": "OLI KOPLING: Volume cukup & sistem berfungsi?", "order": 2},
        {"section": "OLI & RADIATOR", "item": "AIR RADIATOR: Kondisi penuh & tidak ada kebocoran?", "order": 3},
        {"section": "OLI & RADIATOR", "item": "OLI STERING: Oli cukup & kemudi ringan?", "order": 4},

        # SECTION: REM
        {"section": "REM", "item": "DPN/BELAKANG: Fungsi rem bekerja pakem/normal?", "order": 5},
        {"section": "REM", "item": "REM TANGAN: Mampu menahan kendaraan dengan kuat?", "order": 6},

        # SECTION: LAMPU-LAMPU
        {"section": "LAMPU-LAMPU", "item": "BESAR JAUH/DEKAT: Lampu menyala terang?", "order": 7},
        {"section": "LAMPU-LAMPU", "item": "RETING R/L: Lampu sein berfungsi normal?", "order": 8},
        {"section": "LAMPU-LAMPU", "item": "BELAKANG: Lampu senja/kota menyala baik?", "order": 9},
        {"section": "LAMPU-LAMPU", "item": "LAMPU REM: Menyala jelas saat pedal diinjak?", "order": 10},
        {"section": "LAMPU-LAMPU", "item": "MUNDUR: Lampu mundur menyala & berfungsi?", "order": 11},
        {"section": "LAMPU-LAMPU", "item": "ROTARI: Lampu rotari menyala & berputar normal?", "order": 12},

        # SECTION: RODA
        {"section": "RODA", "item": "DEPAN/BELAKANG: Tekanan angin & alur ban layak?", "order": 13},
        {"section": "RODA", "item": "CADANGAN: Ban cadangan tersedia & siap pakai?", "order": 14},

        # SECTION: BODY KABIN
        {"section": "BODY KABIN", "item": "FENDER R/L: Fender baik & tidak penyok/lepas?", "order": 15},
        {"section": "BODY KABIN", "item": "PINTU R/L: Pintu dapat dibuka & dikunci sempurna?", "order": 16},
        {"section": "BODY KABIN", "item": "ATAP KABIN: Kondisi bersih & tidak ada kerusakan?", "order": 17},
        {"section": "BODY KABIN", "item": "JOK: Bersih, tidak sobek & pengaturan berfungsi?", "order": 18},
        {"section": "BODY KABIN", "item": "LANTAI KABIN: Bersih dari kotoran & sampah?", "order": 19},
        {"section": "BODY KABIN", "item": "KARET MOUNTING: Utuh & tidak pecah-pecah?", "order": 20},

        # SECTION: TOOLS
        {"section": "TOOLS", "item": "DONGKRAK: Tersedia & berfungsi?", "order": 21},
        {"section": "TOOLS", "item": "KONCI RODA: Tersedia & sesuai ukuran?", "order": 22},
        {"section": "TOOLS", "item": "SEGITIGA PENGAMAN: Tersedia kondisi baik?", "order": 23},
        {"section": "TOOLS", "item": "TRAFFIC CONE: Tersedia & layak sebagai tanda?", "order": 24},
        {"section": "TOOLS", "item": "AC: Berfungsi dingin & normal?", "order": 25},

        # SECTION: OTHERS
        {"section": "OTHERS", "item": "SABUK PENGAMAN: Mengunci baik & tidak macet?", "order": 26},
        {"section": "OTHERS", "item": "SPIDOMETER: Panel indikator berfungsi akurat?", "order": 27},
        {"section": "OTHERS", "item": "KLAKSON: Suara nyaring & berfungsi baik?", "order": 28},
        {"section": "OTHERS", "item": "SPION: Lengkap, bersih & mudah diatur?", "order": 29},
        {"section": "OTHERS", "item": "WIPER: Karet bagus & sapuan bersih?", "order": 30},
        {"section": "OTHERS", "item": "AIR WIPER: Terisi penuh & nosel tidak tersumbat?", "order": 31},
        {"section": "OTHERS", "item": "ALAREM MUNDUR: Berbunyi jelas saat mundur?", "order": 32},
        {"section": "OTHERS", "item": "RADIO KOMUNIKASI: Berfungsi kirim & terima sinyal?", "order": 33},
        {"section": "OTHERS", "item": "KNALPOT: Standar, tidak bocor & terpasang kuat?", "order": 34},
        {"section": "OTHERS", "item": "NO LAMBUNG: Terlihat jelas & tidak pudar?", "order": 35},
        {"section": "OTHERS", "item": "APAR: Tersedia, segel utuh & tekanan hijau?", "order": 36},

        # SECTION: SURAT-SURAT & KESELAMATAN
        {"section": "SURAT-SURAT", "item": "P3K: Kotak P3K lengkap & tidak kadaluwarsa?", "order": 37},
        {"section": "SURAT-SURAT", "item": "STNK: Asli/Fotokopi tersedia & masa berlaku aktif?", "order": 38},
        {"section": "SURAT-SURAT", "item": "KIR: Masih berlaku & sudah uji berkala?", "order": 39},
    ]

    for data in items_to_seed:
        # Cek duplikasi agar tidak error saat dijalankan ulang
        existing = db.query(ChecklistTemplate).filter_by(item_name=data["item"]).first()
        
        if not existing:
            new_item = ChecklistTemplate(
                item_name=data["item"],
                section_name=data["section"],
                item_order=data["order"],
                # Menerapkan Tagging ARRAY
                vehicle_tags=all_vehicles, 
                applicable_shifts=all_shifts,
                options=default_options,
                is_active=True
            )
            db.add(new_item)

    db.commit()
    print(f"✅ Berhasil menambahkan {len(items_to_seed)} item checklist ke database.")

def main():
    db = SessionLocal()
    try:
        seed_p2h_checklists(db)
        print("\n🎉 Seeding finished successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()