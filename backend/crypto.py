import base64
import os
from Crypto.Cipher import AES, ChaCha20_Poly1305
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

DEFAULT_ITERATIONS = 600000

def derive_key(password: str, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    """Menurunkan kunci 256-bit dari password menggunakan PBKDF2-HMAC-SHA256."""
    return PBKDF2(password, salt, dkLen=32, count=iterations, hmac_hash_module=SHA256)

def encrypt_data(
    data: bytes,
    password: str,
    algorithm: str = "aes-gcm",
    salt: bytes = None,
    nonce: bytes = None,
    iterations: int = DEFAULT_ITERATIONS
) -> dict:
    algo_clean = algorithm.lower().replace("_", "-")
    if algo_clean not in ["aes-gcm", "chacha20-poly1305"]:
        raise ValueError(f"Algoritma '{algorithm}' tidak didukung.")

    if salt is None:
        salt = get_random_bytes(16)
        
    key = derive_key(password, salt, iterations)

    if algo_clean == "aes-gcm":
        if nonce is None:
            nonce = get_random_bytes(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    else:
        if nonce is None:
            nonce = get_random_bytes(12)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)

    ciphertext, tag = cipher.encrypt_and_digest(data)

    return {
        "algorithm": algo_clean,
        "salt": base64.b64encode(salt).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "tag": base64.b64encode(tag).decode("utf-8"),
        "iterations": iterations
    }

def decrypt_data(data_dict: dict, password: str) -> bytes:
    algorithm = data_dict.get("algorithm", "aes-gcm").lower().replace("_", "-")
    salt = base64.b64decode(data_dict["salt"])
    nonce = base64.b64decode(data_dict["nonce"])
    ciphertext = base64.b64decode(data_dict["ciphertext"])
    tag = base64.b64decode(data_dict["tag"])
    iterations = data_dict.get("iterations", DEFAULT_ITERATIONS)

    key = derive_key(password, salt, iterations)

    if algorithm == "aes-gcm":
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    elif algorithm == "chacha20-poly1305":
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    else:
        raise ValueError(f"Algoritma '{algorithm}' tidak dikenali.")

    return cipher.decrypt_and_verify(ciphertext, tag)

def encrypt_file_gcm(data: bytes, password: str, salt: bytes = None, nonce: bytes = None) -> dict:
    return encrypt_data(data, password, algorithm="aes-gcm", salt=salt, nonce=nonce)

def decrypt_file_gcm(data_dict: dict, password: str) -> bytes:
    return decrypt_data(data_dict, password)

def encrypt_bmp_ecb(bmp_bytes: bytes, password: str) -> bytes:
    if len(bmp_bytes) < 54 or bmp_bytes[:2] != b'BM':
        raise ValueError("Data bukan berkas BMP yang valid.")

    header = bmp_bytes[:54]
    pixels = bmp_bytes[54:]

    padding_len = 16 - (len(pixels) % 16)
    if padding_len != 16:
        pixels += b"\x00" * padding_len

    salt = b"DEMO_ECB_SALT123"
    key = derive_key(password, salt, iterations=100000)
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_pixels = cipher.encrypt(pixels)

    return header + encrypted_pixels[:len(bmp_bytes) - 54]