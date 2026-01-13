import bcrypt
from datetime import date

def hash_password(password: str) -> str:
    """
    Mengubah password mentah menjadi hash (bcrypt).
    Bcrypt hanya menerima max 72 bytes.
    """
    # Encode dan truncate ke 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi apakah password cocok dengan hash.
    """
    # Encode dan truncate ke 72 bytes
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# --- FUNGSI INI DIKEMBALIKAN AGAR TIDAK ERROR IMPORT ---
def generate_username(first_name: str, birth_date: date) -> str:
    """
    Membuat username dari nama depan + tanggal lahir.
    Contoh: Budi + 1990-05-15 -> budi15051990
    
    Catatan: Fungsi ini dipertahankan agar auth_service.py tidak error,
    meskipun kolom 'username' mungkin sudah tidak dipakai di database.
    """
    # Safety check jika birth_date kosong
    if not birth_date:
        # Fallback hanya pakai nama
        return first_name.lower().replace(" ", "")
        
    # Ambil tanggal format DDMMYYYY
    date_str = birth_date.strftime("%d%m%Y")
    
    # Ambil kata pertama dari nama, lowercase
    first_name_clean = first_name.split()[0].lower()
    
    # Gabung
    username = f"{first_name_clean}{date_str}"
    
    return username