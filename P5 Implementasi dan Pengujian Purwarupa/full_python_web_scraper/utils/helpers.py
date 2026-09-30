# utils/helpers.py
import re
from datetime import datetime

def clean_text(text: str) -> str:
    """Membersihkan teks dari spasi berlebih dan karakter aneh."""
    return re.sub(r"\s+", " ", text).strip()

def validate_url(url: str) -> bool:
    """Validasi sederhana apakah string adalah URL."""
    return url.startswith("http://") or url.startswith("https://")

def get_timestamp() -> str:
    """Menghasilkan timestamp saat ini dalam format ISO."""
    return datetime.now().isoformat()

