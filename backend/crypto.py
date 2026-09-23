import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def derive_key(password: str, salt: bytes) -> bytes:
    """Menurunkan kata sandi menjadi kunci AES 256-bit menggunakan PBKDF2."""
    return PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)

def encrypt_file_gcm(data: bytes, password: str) -> dict:
    """Enkripsi standar berkas/teks menggunakan AES-256-GCM (Fitur Wajib)."""
    salt = get_random_bytes(16)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    return {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "nonce": base64.b64encode(cipher.nonce).decode('utf-8'),
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "tag": base64.b64encode(tag).decode('utf-8')
    }

def decrypt_file_gcm(encrypted_data: dict, password: str) -> bytes:
    """Dekripsi berkas/teks dengan verifikasi tag AES-GCM (Fitur Wajib)."""
    salt = base64.b64decode(encrypted_data["salt"])
    nonce = base64.b64decode(encrypted_data["nonce"])
    ciphertext = base64.b64decode(encrypted_data["ciphertext"])
    tag = base64.b64decode(encrypted_data["tag"])
    
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    # Otomatis melempar ValueError jika tag salah atau ciphertext diubah (tamper)
    return cipher.decrypt_and_verify(ciphertext, tag)

def encrypt_bmp_visual(bmp_bytes: bytes, password: str) -> dict:
    """
    Enkripsi Citra dengan memisahkan 54 byte header BMP (Fitur Pengayaan).
    Mengembalikan dua citra: hasil mode ECB (pola terlihat) dan mode GCM (noise acak).
    """
    if len(bmp_bytes) <= 54:
        raise ValueError("Ukuran berkas BMP tidak valid atau terlalu kecil.")
    
    # 1. Pisahkan Header BMP (54 byte pertama) dari Piksel
    header = bmp_bytes[:54]
    pixels = bmp_bytes[54:]
    
    salt = get_random_bytes(16)
    key = derive_key(password, salt)
    
    # --- Mode 1: AES-ECB (Pembanding Visual) ---
    padded_pixels = pad(pixels, AES.block_size)
    cipher_ecb = AES.new(key, AES.MODE_ECB)
    ecb_enc_pixels = cipher_ecb.encrypt(padded_pixels)[:len(pixels)]
    ecb_bmp = header + ecb_enc_pixels
    
    # --- Mode 2: AES-256-GCM (Mode Aman) ---
    cipher_gcm = AES.new(key, AES.MODE_GCM)
    gcm_enc_pixels, _ = cipher_gcm.encrypt_and_digest(pixels)
    gcm_bmp = header + gcm_enc_pixels
    
    return {
        "ecb_image_base64": base64.b64encode(ecb_bmp).decode('utf-8'),
        "gcm_image_base64": base64.b64encode(gcm_bmp).decode('utf-8')
    }