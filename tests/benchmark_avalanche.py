import os
import sys
import base64
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.crypto import encrypt_data
from backend.metrics import calculate_avalanche_effect

def flip_bit(data: bytes, bit_index: int) -> bytes:
    data_bytearray = bytearray(data)
    byte_idx = bit_index // 8
    bit_idx = bit_index % 8
    data_bytearray[byte_idx] ^= (1 << bit_idx)
    return bytes(data_bytearray)

def test_avalanche_key_change(algorithm="aes-gcm", iterations=100) -> float:
    salt = b"FIXED_SALT_12345"
    nonce = b"FIXED_NONCE1"
    plaintext = b"Ini adalah teks pengujian murni untuk Avalanche Effect Kriptografi UTS."
    password = "PasswordUtama123!"
    
    enc_base = encrypt_data(plaintext, password, algorithm=algorithm, salt=salt, nonce=nonce)
    c_base = base64.b64decode(enc_base["ciphertext"]) + base64.b64decode(enc_base["tag"])
    
    total_avalanche = 0.0
    
    for _ in range(iterations):
        pass_bytes = password.encode('utf-8')
        bit_to_flip = random.randint(0, len(pass_bytes) * 8 - 1)
        modified_pass_bytes = flip_bit(pass_bytes, bit_to_flip)
        
        modified_pass = modified_pass_bytes.decode('utf-8', errors='ignore')
        if not modified_pass or modified_pass == password:
            modified_pass = password + "x"
            
        enc_mod = encrypt_data(plaintext, modified_pass, algorithm=algorithm, salt=salt, nonce=nonce)
        c_mod = base64.b64decode(enc_mod["ciphertext"]) + base64.b64decode(enc_mod["tag"])
        
        avalanche = calculate_avalanche_effect(c_base, c_mod)
        total_avalanche += avalanche
        
    return total_avalanche / iterations

def test_avalanche_plaintext_change(algorithm="aes-gcm", iterations=100) -> float:
    salt = b"FIXED_SALT_12345"
    nonce = b"FIXED_NONCE1"
    plaintext = b"Ini adalah teks pengujian murni untuk Avalanche Effect Kriptografi UTS."
    password = "PasswordUtama123!"
    
    enc_base = encrypt_data(plaintext, password, algorithm=algorithm, salt=salt, nonce=nonce)
    c_base = base64.b64decode(enc_base["ciphertext"]) + base64.b64decode(enc_base["tag"])
    
    total_avalanche = 0.0
    
    for _ in range(iterations):
        bit_to_flip = random.randint(0, len(plaintext) * 8 - 1)
        modified_plaintext = flip_bit(plaintext, bit_to_flip)
        
        enc_mod = encrypt_data(modified_plaintext, password, algorithm=algorithm, salt=salt, nonce=nonce)
        c_mod = base64.b64decode(enc_mod["ciphertext"]) + base64.b64decode(enc_mod["tag"])
        
        avalanche = calculate_avalanche_effect(c_base, c_mod)
        total_avalanche += avalanche
        
    return total_avalanche / iterations

def run_benchmark():
    print("--- UJI AVALANCHE EFFECT MURNI ---")
    for algo in ["aes-gcm", "chacha20-poly1305"]:
        try:
            avg_key = test_avalanche_key_change(algo, 100)
            avg_plain = test_avalanche_plaintext_change(algo, 100)
            print(f"\nAlgoritma: {algo.upper()}")
            print(f"  - Perubahan 1 Bit Kunci     (Rata-rata 100x): {avg_key:.2f}% (Target: ~50%)")
            print(f"  - Perubahan 1 Bit Plainteks (Rata-rata 100x): {avg_plain:.4f}%")
        except Exception as e:
            print(f"\nAlgoritma: {algo.upper()} -> Error: {e}")

if __name__ == "__main__":
    run_benchmark()