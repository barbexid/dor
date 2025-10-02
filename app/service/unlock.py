import os
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Lokasi file unlock_status.json
UNLOCK_FILE = os.path.join(os.path.dirname(__file__), "unlock_status.json")

# Kunci rahasia (harus 16, 24, atau 32 byte untuk AES)
SECRET_KEY = b'barbex_id_secret!'  # 16-byte key, ubah sesuai kebutuhan

def encrypt_base64(data: dict) -> str:
    raw = json.dumps(data).encode()
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(raw, AES.block_size))
    return base64.b64encode(encrypted).decode()

def decrypt_base64(encoded_data: str) -> dict:
    try:
        encrypted = base64.b64decode(encoded_data.encode())
        cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
        return json.loads(decrypted.decode())
    except Exception:
        return {"is_unlocked": False}

def load_unlock_status():
    if not os.path.exists(UNLOCK_FILE):
        return {"is_unlocked": False}
    try:
        with open(UNLOCK_FILE, "r") as f:
            encoded_data = f.read().strip()
        return decrypt_base64(encoded_data)
    except Exception:
        return {"is_unlocked": False}

def save_unlock_status(status: bool):
    encoded = encrypt_base64({"is_unlocked": status})
    with open(UNLOCK_FILE, "w") as f:
        f.write(encoded)
