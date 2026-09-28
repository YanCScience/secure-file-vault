import hashlib
import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.crypto import encrypt_data, decrypt_data

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

BERKAS_NYATA = [
    "sample_1kb.txt", "sample.pdf", "sampel2.pdf", "sample.bmp",
    "sample.png", "sampel3.png", "sample.jpg", "sampel2.jpg",
]

MASUKAN_SINTETIS = {
    "teks_unicode": "Kriptografi modern: AES-256-GCM dan ChaCha20 \U0001F510 - aman!".encode("utf-8"),
    "semua_nilai_byte": bytes(range(256)),
}

ALGORITMA = ["aes-gcm", "chacha20-poly1305"]


def _muat_masukan():
    masukan = {}
    for nama in BERKAS_NYATA:
        with open(os.path.join(DATA_DIR, nama), "rb") as f:
            masukan[nama] = f.read()
    masukan.update(MASUKAN_SINTETIS)
    return masukan


MASUKAN = _muat_masukan()


def test_jumlah_masukan_minimal_10():
    assert len(MASUKAN) >= 10


@pytest.mark.parametrize("algoritma", ALGORITMA)
@pytest.mark.parametrize("nama", list(MASUKAN))
def test_dekripsi_benar(nama, algoritma):
    password = "SandiUji10Input!"
    data = MASUKAN[nama]
    paket = encrypt_data(data, password, algorithm=algoritma)
    hasil = decrypt_data(paket, password)
    assert hashlib.sha256(hasil).hexdigest() == hashlib.sha256(data).hexdigest()