import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.crypto import encrypt_file_gcm, decrypt_file_gcm
from backend.metrics import calculate_byte_histogram, calculate_entropy, calculate_avalanche_effect

def generate_dummy_file(size_in_mb: float) -> bytes:
    return os.urandom(int(size_in_mb * 1024 * 1024))

def benchmark_encryption():
    sizes = [0.001, 1.0, 10.0] # 1 KB, 1 MB, 10 MB
    print("----- UJI WAKTU EKSEKUSI AES-256-GCM -----")
    for sz in sizes:
        data = generate_dummy_file(sz)
        start = time.time()
        enc = encrypt_file_gcm(data, "sandi123")
        enc_time = (time.time() - start) * 1000
        
        start = time.time()
        decrypt_file_gcm(enc, "sandi123")
        dec_time = (time.time() - start) * 1000
        
        print(f"Ukuran: {sz} MB | Enkripsi: {enc_time:.2f} ms | Dekripsi: {dec_time:.2f} ms")

def benchmark_avalanche_and_entropy():
    print("\n----- UJI AVALANCHE EFFECT & ENTROPI -----")
    plain = b"Pengujian Avalanche Effect dan Entropi Kriptografi"
    enc1 = encrypt_file_gcm(plain, "sandi123")
    enc2 = encrypt_file_gcm(plain, "sandi124") 
    
    import base64
    c1 = base64.b64decode(enc1["ciphertext"])
    c2 = base64.b64decode(enc2["ciphertext"])
    
    avalanche = calculate_avalanche_effect(c1, c2)
    entropy_plain = calculate_entropy(plain)
    entropy_cipher = calculate_entropy(c1)

    hist_plain = calculate_byte_histogram(plain)
    hist_cipher = calculate_byte_histogram(c1)
    
    print(f"Avalanche Effect (Beda 1 Bit Kunci): {avalanche:.2f}%")
    print(f"Entropi Plainteks : {entropy_plain:.4f}")
    print(f"Entropi Cipherteks: {entropy_cipher:.4f} (Mendekati 8.0 = Ideal)")
    print(f"Distribusi Histogram Plainteks (10 byte pertama): {hist_plain['distribution'][:10]}")
    print(f"Distribusi Histogram Cipherteks (10 byte pertama): {hist_cipher['distribution'][:10]}")

if __name__ == "__main__":
    benchmark_encryption()
    benchmark_avalanche_and_entropy()