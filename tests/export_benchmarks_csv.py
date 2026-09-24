import csv
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.crypto import encrypt_file_gcm, decrypt_file_gcm
from backend.metrics import calculate_entropy, calculate_avalanche_effect

def run_csv_export():
    csv_file = "hasil_pengujian_kriptografi.csv"
    
    # Menyiapkan berkas uji (1 KB, 1 MB, 10 MB, dan sampel teks)
    sample_files = {
        "1 KB Dummy": os.urandom(1024),
        "1 MB Dummy": os.urandom(1024 * 1024),
        "10 MB Dummy": os.urandom(10 * 1024 * 1024),
        "Dokumen PDF": b"%PDF-1.4 Header PDF Dummy untuk pengujian laporan teknis Aisyah...",
        "Gambar BMP Header": b"BM" + b"\x00" * 52 + os.urandom(500)
    }
    
    password = "SandiUjiLaporan123!"
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Nama Berkas / Skenario", "Ukuran (Bytes)", "Waktu Enkripsi (ms)", "Waktu Dekripsi (ms)", "Entropi Cipherteks", "Avalanche Effect (%)"])
        
        for name, data in sample_files.items():
            # Enkripsi & Waktu
            start_enc = time.time()
            enc = encrypt_file_gcm(data, password)
            enc_time = (time.time() - start_enc) * 1000
            
            # Dekripsi & Waktu
            start_dec = time.time()
            decrypt_file_gcm(enc, password)
            dec_time = (time.time() - start_dec) * 1000
            
            # Avalanche Effect (Beda 1 bit pada kunci)
            enc_mod = encrypt_file_gcm(data, "SandiUjiLaporan123\"")
            import base64
            c1 = base64.b64decode(enc["ciphertext"])
            c2 = base64.b64decode(enc_mod["ciphertext"])
            avalanche = calculate_avalanche_effect(c1, c2)
            
            # Entropi
            entropy = calculate_entropy(c1)
            
            writer.writerow([name, len(data), round(enc_time, 2), round(dec_time, 2), round(entropy, 4), round(avalanche, 2)])
            
    print(f"Hasil pengujian berhasil disimpan ke berkas '{csv_file}'!")

if __name__ == "__main__":
    run_csv_export()