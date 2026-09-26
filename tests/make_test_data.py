import os

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

def main():
    ensure_data_dir()
    generate_text_file("sample_1kb.txt", 1024)
    generate_text_file("sample_1mb.txt", 1024 * 1024)
    generate_text_file("sample_10mb.txt", 10 * 1024 * 1024)

    print("\n[SUCCESS] Berkas teks 1 KB/1 MB/10 MB sudah dibuat.")
    
if __name__ == "__main__":
    main()