# Secure File Vault & Citra Visualizer (ECB vs GCM)

Aplikasi kriptografi untuk mengenkripsi dan mendekripsi teks maupun berkas dengan algoritma modern (AES-256-GCM dan ChaCha20-Poly1305), serta memvisualisasikan perbandingan mode ECB vs GCM pada citra.

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

## Contoh Penggunaan

Setelah backend (`uvicorn backend.main:app --reload`) menyala di `http://localhost:8000`
dan `frontend/index.html` dibuka di browser, ada tiga mode yang bisa dicoba:

### 1. Enkripsi & Dekripsi Berkas

**Mengunci berkas:**
1. Pastikan tab **Berkas** aktif (default) pada bagian "1. Siapkan data".
2. Klik kotak unggah lalu pilih berkas apa saja (PDF, gambar, dokumen, dll), atau
   seret-lepas (drag & drop) langsung ke kotaknya.
3. Isi kata sandi pada kolom "Kata sandi".
4. Pilih algoritma (AES-256-GCM atau ChaCha20-Poly1305).
5. Klik **Kunci berkas**.
6. Cipherteks (Base64) tampil di panel "2. Hasil", dan tombol **↓ Unduh hasil**
   muncul untuk menyimpan berkas `.svault` (berisi ciphertext, salt, nonce, dan tag —
   password TIDAK ikut disimpan).

**Membuka berkas:**
1. Unggah berkas `.svault` yang tadi diunduh.
2. Masukkan kata sandi yang sama persis seperti saat mengunci.
3. Klik **Buka berkas**.
4. Jika kata sandi benar dan berkas tidak diubah, tombol **↓ Unduh hasil** muncul
   berisi berkas asli.
5. Jika kata sandi salah atau isi `.svault` diubah, aplikasi menampilkan notifikasi
   error dan menolak dekripsi.

### 2. Enkripsi & Dekripsi Teks

1. Klik tab **Teks** pada bagian "1. Siapkan data" untuk beralih dari mode berkas.
2. Ketik atau tempel teks pada kotak yang muncul.
3. Isi kata sandi, pilih algoritma, lalu klik **Kunci teks**.
4. Hasilnya berupa JSON utuh (`algorithm`, `salt`, `nonce`, `ciphertext`, `tag`,
   `iterations`) yang tampil di panel "2. Hasil" — klik **Salin** untuk menyalinnya.
5. Untuk membuka kembali: tempel JSON hasil tadi ke kotak teks (menggantikan teks
   asli), isi kata sandi yang sama, lalu klik **Buka teks**. Teks asli akan tampil
   di panel "2. Hasil".

> Mode ini memakai endpoint backend `POST /api/encrypt-text` dan `POST /api/decrypt-text`,
> terpisah dari endpoint berkas karena payload-nya JSON langsung, bukan multipart file upload.

### 3. Uji Tamper (Bukti Deteksi Perubahan Data)

Setelah berhasil mengunci berkas **atau** teks (langkah 1 atau 2 di atas), tombol
**⚠ Uji tamper (ubah 1 byte)** akan muncul di panel "2. Hasil". Fitur ini menggantikan
kebutuhan mengedit `.svault` secara manual untuk menunjukkan skenario demo wajib
("ubah satu byte cipherteks lalu tunjukkan penolakan"):

1. Pastikan kolom kata sandi masih terisi kata sandi yang **benar** (dipakai ulang
   untuk memastikan penolakan murni karena data diubah, bukan karena kata sandi salah).
2. Klik **⚠ Uji tamper (ubah 1 byte)**.
3. Aplikasi otomatis membalik satu bit pada byte pertama `ciphertext` (atau `tag`
   bila cipherteks kosong), lalu mengirim hasilnya untuk didekripsi.
4. Panel "2. Hasil" menampilkan laporan ringkas: bidang yang diubah, nilai sebelum/sesudah,
   dan status akhirnya — seharusnya **DITOLAK** karena auth tag gagal diverifikasi.

### 4. Demo Visualisasi ECB vs GCM (Fitur Pengayaan)

1. Buka bagian **Image Crypto Visualization** (bisa lompat langsung lewat menu
   "Visualisasi Enkripsi" di navbar).
2. Unggah sebuah gambar (PNG/JPG/BMP/GIF/WebP) dan isi kata sandi bebas.
3. Klik **Compare / Encrypt Image**.
4. Tiga gambar tampil berdampingan: **Original**, **AES-ECB**, dan **AES-GCM**,
   masing-masing dengan nilai entropinya.
5. Pada gambar dengan area warna solid/berulang, hasil **AES-ECB** masih memperlihatkan
   pola bentuk aslinya (bukti mode ECB tidak aman), sedangkan **AES-GCM** tampak
   seperti derau acak sepenuhnya.

> Catatan: mode ECB di sini **sengaja** dipakai untuk demonstrasi kelemahan, sesuai
> larangan pemakaian ECB untuk fitur keamanan utama pada ketentuan tugas. Gambar pada
> bagian ini tidak dirancang untuk didekripsi kembali — fungsinya murni perbandingan visual.