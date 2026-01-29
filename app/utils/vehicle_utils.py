"""
Vehicle Utility Functions
Utility functions untuk pemrosesan data kendaraan
"""

import re
from typing import Optional


def normalize_hull_number(hull_number: str) -> str:
    """
    Normalize nomor lambung untuk searching dan comparison.
    Menghapus spasi, titik, koma, dan karakter khusus lainnya.
    Convert ke uppercase.
    
    Contoh:
        "P 309" -> "P309"
        "p.309" -> "P309"
        "P,309" -> "P309"
        "  P  .  309  " -> "P309"
    
    Args:
        hull_number: Nomor lambung dalam format apapun
        
    Returns:
        Normalized hull number (uppercase, tanpa separator)
    """
    if not hull_number:
        return ""
    
    # Hapus spasi, titik, koma, dash, dan karakter khusus lainnya
    # Hanya keep alphanumeric
    normalized = re.sub(r'[^a-zA-Z0-9]', '', hull_number)
    
    # Convert ke uppercase
    return normalized.upper()


def format_hull_number(hull_number: str) -> str:
    """
    Format nomor lambung ke format standar: [HURUF].[ANGKA]
    Contoh: "P309" -> "P.309", "A21" -> "A.21"
    
    Args:
        hull_number: Nomor lambung dalam format apapun
        
    Returns:
        Formatted hull number dengan titik separator
    """
    if not hull_number:
        return ""
    
    # Normalize dulu untuk clean the input
    normalized = normalize_hull_number(hull_number)
    
    # Extract letter prefix dan number part
    # Asumsikan format: satu atau lebih huruf diikuti angka
    match = re.match(r'^([A-Z]+)(\d+)$', normalized)
    
    if match:
        letter_part = match.group(1)
        number_part = match.group(2)
        return f"{letter_part}.{number_part}"
    
    # Jika tidak match pattern, return normalized value
    return normalized


def is_hull_number_match(input_hull: str, stored_hull: str) -> bool:
    """
    Compare dua nomor lambung dengan normalisasi.
    Mengabaikan format, case, dan separator.
    
    Args:
        input_hull: Nomor lambung yang diinput user
        stored_hull: Nomor lambung yang tersimpan di database
        
    Returns:
        True jika match (setelah normalisasi)
    """
    if not input_hull or not stored_hull:
        return False
    
    return normalize_hull_number(input_hull) == normalize_hull_number(stored_hull)


def validate_hull_number_format(hull_number: str) -> tuple[bool, Optional[str]]:
    """
    Validasi format nomor lambung.
    Format yang valid: huruf + angka (bisa dengan atau tanpa separator)
    
    Args:
        hull_number: Nomor lambung untuk divalidasi
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not hull_number:
        return False, "Nomor lambung tidak boleh kosong"
    
    # Normalize untuk validasi
    normalized = normalize_hull_number(hull_number)
    
    # Check jika kosong setelah normalisasi
    if not normalized:
        return False, "Nomor lambung tidak valid (hanya berisi karakter khusus)"
    
    # Check format: harus ada huruf dan angka
    if not re.match(r'^[A-Z]+\d+$', normalized):
        return False, "Format nomor lambung harus: huruf + angka (contoh: P309, A21, B030)"
    
    return True, None
