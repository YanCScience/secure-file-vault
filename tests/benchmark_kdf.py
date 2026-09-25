import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.crypto import derive_key, encrypt_data
from Crypto.Random import get_random_bytes

password = "sandi123"
salt = get_random_bytes(16)
plaintext = os.urandom(1024)  # 1 KB, biar enkripsi murninya kelihatan cepat
iterations = 600000
runs = 5

kdf_times = []
enc_times = []

for _ in range(runs):
    start = time.time()
    key = derive_key(password, salt, iterations)
    kdf_times.append((time.time() - start) * 1000)

    start = time.time()
    encrypt_data(plaintext, password, salt=salt, iterations=1)  # iterations=1 biar KDF-nya nggak ikut kehitung besar
    enc_times.append((time.time() - start) * 1000)

avg_kdf = sum(kdf_times) / runs
avg_enc = sum(enc_times) / runs

print(f"Rata-rata waktu KDF (PBKDF2, {iterations} iterasi): {avg_kdf:.2f} ms")
print(f"Rata-rata waktu enkripsi AES-GCM murni (1 iterasi KDF, jadi hampir 0): {avg_enc:.2f} ms")
print(f"Proporsi waktu KDF terhadap total: {avg_kdf/(avg_kdf+avg_enc)*100:.1f}%")