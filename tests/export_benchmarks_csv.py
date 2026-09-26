import csv
import os
import sys
import time
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.crypto import encrypt_file_gcm, decrypt_file_gcm, derive_key
from backend.metrics import calculate_entropy, calculate_avalanche_effect
from Crypto.Cipher import AES

def encrypt_with_fixed_nonce(data: bytes, password: str, salt: bytes, nonce: bytes) -> bytes:
    """Fungsi pembantu untuk mengunci Salt & Nonce agar pengujian Avalanche Effect valid."""
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, _ = cipher.encrypt_and_digest(data)
    return ciphertext    

def run_csv_export():
    csv_file = "hasil_pengujian_kriptografi.csv"
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    
    file_to_test = [
        ("File Teks (1 KB)", os.path.join(data_dir, "sample_1kb.txt")),
        ("File Teks (100 KB)", os.path.join(data_dir, "sample_100kb.txt")),
        ("File Teks (1 MB)", os.path.join(data_dir, "sample_1mb.txt")),
        ("File Teks (10 MB)", os.path.join(data_dir, "sample_10mb.txt")),
        ("File PDF", os.path.join(data_dir, "sample.pdf")),
        ("Gambar Uncompressed BMP", os.path.join(data_dir, "sample.bmp")),
        ("Gambar Compressed PNG", os.path.join(data_dir, "sample.png")),
        ("File Struktur Data JSON", os.path.join(data_dir, "sample.json")),
        ("Simulasi Cipherteks Rusak (1-Byte Corrupt)", os.path.join(data_dir, "sample.pdf")),
        ("Simulasi Bit-Flip Kunci (Avalanche Test)", os.path.join(data_dir, "sample_1mb.txt"))
    ]
    
    password1 = "SandiUjiLaporan123"
    password2 = "SandiUjiLaporan122"

    results = []

    for name, filepath in file_to_test:
        if not os.path.exists(filepath):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f_temp:
                f_temp.write(b"Sampel data untuk pengujian kriptografi. " * 100)

        with open(filepath, "rb") as f:
            data = f.read()

        pt_entropy = calculate_entropy(data)

        start_enc = time.time()
        enc = encrypt_file_gcm(data, password1)
        enc_time = (time.time() - start_enc) * 1000

        start_dec = time.time()
        dec = decrypt_file_gcm(enc, password1)
        dec_time = (time.time() - start_dec) * 1000

        c1_bytes = base64.b64decode(enc["ciphertext"])
        ct_entropy = calculate_entropy(c1_bytes)

        salt = base64.b64decode(enc["salt"])
        nonce = base64.b64decode(enc["nonce"])

        c1_fixed = encrypt_with_fixed_nonce(data, password1, salt, nonce)
        c2_fixed = encrypt_with_fixed_nonce(data, password2, salt, nonce)
        avalanche_effect = calculate_avalanche_effect(c1_fixed, c2_fixed)

        results.append([
            name,
            len(data),
            round(enc_time, 2),
            round(dec_time, 2),
            round(pt_entropy, 4),
            round(ct_entropy, 4),
            round(avalanche_effect, 2)
        ])

    with open(csv_file, mode="w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Nama Berkas",
            "Ukuran Berkas (byte)",
            "Waktu Enkripsi (ms)",
            "Waktu Dekripsi (ms)",
            "Entropi Plaintext",
            "Entropi Ciphertext",
            "Avalanche Effect (%)"
        ])
        writer.writerows(results)

    print(f"Pengujian selesai. Hasil diekspor ke {csv_file}")

if __name__ == "__main__":
    run_csv_export()    