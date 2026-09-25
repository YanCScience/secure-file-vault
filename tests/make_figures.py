import sys
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.crypto import encrypt_data, encrypt_bmp_ecb

BMP_PATH = ROOT / "tests" / "data" / "sample.bmp"
OUT_DIR = ROOT / "docs"
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "histogram_ecb_vs_gcm.png"

PASSWORD = "sandi123"

with open(BMP_PATH, "rb") as f:
    bmp_bytes = f.read()

pixel_data = bmp_bytes[54:]  # skip 54-byte BMP header

gcm_result = encrypt_data(pixel_data, PASSWORD, algorithm="aes-gcm")
import base64
gcm_ciphertext = base64.b64decode(gcm_result["ciphertext"])

ecb_full = encrypt_bmp_ecb(bmp_bytes, PASSWORD)
ecb_ciphertext = ecb_full[54:]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
datasets = [
    ("Plainteks (Asli)", pixel_data, "gray"),
    ("AES-ECB", ecb_ciphertext, "red"),
    ("AES-GCM", gcm_ciphertext, "blue"),
]

for ax, (title, data, color) in zip(axes, datasets):
    ax.hist(list(data), bins=256, range=(0, 255), color=color, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Nilai Byte (0-255)")
    ax.set_ylabel("Frekuensi")

fig.suptitle("Distribusi Frekuensi Byte: Plainteks vs AES-ECB vs AES-GCM", fontsize=13)
fig.tight_layout()
fig.savefig(OUT_PATH, dpi=150)
print(f"Selesai: {OUT_PATH}")