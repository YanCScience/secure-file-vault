import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.crypto import encrypt_file_gcm, decrypt_file_gcm

def test_decrypt_10_different_inputs():
    inputs = [
        b"Teks singkat 1",
        b"Teks lebih panjang untuk menguji karakter unik !@#$%^&*()",
        b"%PDF-1.4 Header PDF buatan untuk simulasi dokumen PDF",
        b"BM54ByteHeaderDummyImageDataPixel1234567890",
        b"JSON Data: {'nama': 'Diyani', 'role': 'Backend'}",
        b"Angka acak " + os.urandom(500),
        b"Berkas 1 KB " + os.urandom(1024),
        b"Berkas 5 KB " + os.urandom(5 * 1024),
        b"Kalimat Indonesia: Kriptografi modern AES-256-GCM sangat aman.",
        b"Kombinasi Byte: " + bytes(range(256))
    ]
    
    password = "SandiUji10Input!"
    
    for idx, data in enumerate(inputs):
        enc = encrypt_file_gcm(data, password)
        data_dict = {
            "salt": enc["salt"],
            "nonce": enc["nonce"],
            "ciphertext": enc["ciphertext"],
            "tag": enc["tag"]
        }
        decrypted = decrypt_file_gcm(data_dict, password)
        assert decrypted == data, f"Gagal dekripsi pada sampel masukan ke-{idx+1}"