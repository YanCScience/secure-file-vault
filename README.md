# Secure File Vault & Citra Visualizer (ECB vs GCM)

Aplikasi kriptografi untuk mengenkripsi dan mendekripsi teks maupun  berkas dengan algoritma modern (AES-256-GCM dan ChaCha20-Poly1305), serta memvisualisasikan perbandingan mode ECB vs GCM pada citra.

## Anggota Kelompok
1. Aisyah Nitiarahma (247006111073)
2. Agniya Azzahra (247006111090)
3. Diyani Rahayu Nur'aeni (247006111115)

## Instalasi
```bash
pip install -r requirements.txt
```

## Menjalankan Backend
Dari root repositori:
```bash
uvicorn backend.main:app --reload
```
Buka http://localhost:8000/docs untuk mencoba API-nya langsung.

## Menjalankan Frontend
Buka `frontend/index.html` langsung di browser.

## Menjalankan Pengujian
Dari root repositori, urutannya **wajib seperti ini**:
```bash
python -m pytest tests -q                  # unit test
python tests/make_test_data.py             # lengkapi berkas 1MB/10MB yang tidak disimpan di Git
python tests/export_benchmarks_csv.py      # hasil waktu, entropi, avalanche -> hasil_pengujian_kriptografi.csv
python tests/csv_to_excel.py               # -> docs/hasil_pengujian_kriptografi.xlsx
```

Catatan: `tests/make_test_data.py` tidak akan menimpa `sample.pdf`, `sample.bmp`,
`sample.png`, `sample.jpg` yang sudah ada di repo — hanya melengkapi berkas teks
1 MB/10 MB yang memang sengaja tidak disimpan di Git karena ukurannya besar.