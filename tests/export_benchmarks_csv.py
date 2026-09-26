import csv
import os
import sys
import time
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.crypto import derive_key, encrypt_data, decrypt_data
from backend.metrics import calculate_entropy, calculate_avalanche_effect
from Crypto.Cipher import AES, ChaCha20_Poly1305

def encrypt_fixed_gcm(data: bytes, password: str, salt: bytes, nonce: bytes) -> bytes:
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, _ = cipher.encrypt_and_digest(data)
    return ciphertext    

def encrypt_fixed_chacha(data: bytes, password: str, salt: bytes, nonce: bytes) -> bytes:
    key = derive_key(password, salt)
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    ciphertext, _ = cipher.encrypt_and_digest(data)
    return ciphertext

def run_csv_export():
    csv_file = "hasil_pengujian_kriptografi.csv"
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    files = [
        ("File Teks 1 KB", os.path.join(data_dir, "sample_1kb.txt")),
        ("File Teks 1 MB", os.path.join(data_dir, "sample_1mb.txt")),
        ("File Teks 10 MB", os.path.join(data_dir, "sample_10mb.txt")),
        ("Dokumen PDF", os.path.join(data_dir, "sample.pdf")),
        ("Gambar BMP", os.path.join(data_dir, "sample.bmp")),
        ("Gambar JPG", os.path.join(data_dir, "sample.jpg")),
        ("Gambar PNG", os.path.join(data_dir, "sample.png"))
    ]
    
    password1 = "SandiUjiLaporan123"
    password2 = "SandiUjiLaporan122"

    results = []

    for name, filepath in files:
        if not os.path.exists(filepath):
            print(f"File tidak ditemukan: {filepath}")
            continue

        with open(filepath, "rb") as f:
            data = f.read()

        pt_entropy = calculate_entropy(data)

        algos = [
            ("AES-256-GCM", "aes-gcm"),
            ("ChaCha20-Poly1305", "chacha20-poly1305")
        ]

        for algo_display, algo_name in algos:
            t0 = time.perf_counter()
            enc = encrypt_data(data, password1, algorithm=algo_name)
            enc_time = (time.perf_counter() - t0) * 1000

            t1 = time.perf_counter()
            dec_data = decrypt_data(enc, password1)
            dec_time = (time.perf_counter() - t1) * 1000

            salt = base64.b64decode(enc["salt"])
            nonce = base64.b64decode(enc["nonce"])

            if algo_name == "aes-gcm":
                c1 = encrypt_fixed_gcm(data, password1, salt, nonce)
                c2 = encrypt_fixed_gcm(data, password2, salt, nonce)
            else:
                c1 = encrypt_fixed_chacha(data, password1, salt, nonce)
                c2 = encrypt_fixed_chacha(data, password2, salt, nonce)

            ct_entropy = calculate_entropy(c1)
            avalanche_effect = calculate_avalanche_effect(c1, c2)
            dec_identical = "Ya" if dec_data == data else "Tidak"

            results.append({
                "Nama Berkas": name,
                "Algoritma": algo_display,
                "Ukuran Berkas (byte)": len(data),
                "Waktu Enkripsi (ms)": round(enc_time, 2),
                "Waktu Dekripsi (ms)": round(dec_time, 2),
                "Entropi Plaintext": round(pt_entropy, 4),
                "Entropi Ciphertext": round(ct_entropy, 4),
                "Avalanche Effect (%)": round(avalanche_effect, 2),
                "Dekripsi Identik": dec_identical
            })

    with open(csv_file, mode="w", newline="", encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"Berhasil mengekspor {len(results)} baris hasil pengujian ke '{csv_file}")

if __name__ == "__main__":
    run_csv_export()    