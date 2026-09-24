import os
from PIL import Image, ImageDraw
from fpdf import FPDF

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def generate_text_file(filename: str, size_in_bytes: int):
    filepath = os.path.join(DATA_DIR, filename)
    base_text = "Laporan Kriptografi Modern UTS Secure File Vault AES-256-GCM dan ChaCha20-Poly1305. "
    repetitions = (size_in_bytes // len(base_text.encode('utf-8'))) + 1
    content = (base_text * repetitions).encode('utf-8')[:size_in_bytes]
    with open(filepath, "wb") as f:
        f.write(content)
    print(f"[+] Berkas teks terbuat: {filename} ({len(content)} bytes)")

def generate_pdf():
    filepath = os.path.join(DATA_DIR, "sample.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="Dokumen Uji Asli UTS Kriptografi", ln=1, align="C")
    pdf.multi_cell(0, 10, txt="Berkas ini digunakan untuk verifikasi dekripsi 100% identik pada format PDF.")
    pdf.output(filepath)
    print(f"[+] Berkas PDF terbuat: sample.pdf ({os.path.getsize(filepath)} bytes)")

def generate_bmp_and_images():
    width, height = 200, 200
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Gambar pola visual untuk pengujian ECB vs GCM
    draw.rectangle([50, 50, 150, 150], fill=(0, 0, 0))
    draw.ellipse([70, 70, 130, 130], fill=(255, 0, 0))

    bmp_path = os.path.join(DATA_DIR, "sample.bmp")
    img.save(bmp_path, format="BMP")
    print(f"[+] Berkas BMP terbuat: sample.bmp ({os.path.getsize(bmp_path)} bytes)")

    png_path = os.path.join(DATA_DIR, "sample.png")
    img.save(png_path, format="PNG")
    print(f"[+] Berkas PNG terbuat: sample.png ({os.path.getsize(png_path)} bytes)")

    jpg_path = os.path.join(DATA_DIR, "sample.jpg")
    img.save(jpg_path, format="JPEG")
    print(f"[+] Berkas JPG terbuat: sample.jpg ({os.path.getsize(jpg_path)} bytes)")

def main():
    ensure_data_dir()
    generate_text_file("sample_1kb.txt", 1024)
    generate_text_file("sample_1mb.txt", 1024 * 1024)
    generate_text_file("sample_10mb.txt", 10 * 1024 * 1024)
    generate_pdf()
    generate_bmp_and_images()
    print("\n[SUCCESS] Seluruh data uji nyata berhasil dibuat di folder 'tests/data'!")

if __name__ == "__main__":
    main()