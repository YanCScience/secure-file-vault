## HASIL DAN PEMBAHASAN

### 1. Hasil Pengujian Kinerja Enkripsi/Dekripsi

Pengujian dilakukan terhadap lima skenario berkas dengan ukuran bervariasi
untuk mengukur waktu eksekusi algoritma AES-256-GCM.

| Berkas/Skenario   | Ukuran (Bytes) | Waktu Enkripsi (ms) | Waktu Dekripsi (ms) | Entropi Cipherteks | Avalanche Effect (%) |
|-------------------|----------------|---------------------|---------------------|--------------------|----------------------|
| 1 KB Dummy        |      1.024     |        605,35       |        563,42       |       7,8326       |         50,04        |
| 1 MB Dummy        |    1.048.576   |        482,60       |        494,59       |       7,9998       |         50,03        |
| 10 MB Dummy       |   10.485.760   |        679,44       |        558,46       |       8,0000       |         50,00        |
| Dokumen PDF       |       66       |        495,74       |        489,12       |       5,8323       |         47,35        |
| Gambar BMP Header |      554       |        483,78       |        501,74       |       7,6163       |         49,71        |

Data lengkap dan grafik perbandingan waktu enkripsi vs dekripsi dapat dilihat
pada `docs/hasil_pengujian_kriptografi.xlsx`.

Dari tabel di atas terlihat bahwa waktu enkripsi dan dekripsi relatif stabil
di kisaran 480–680 ms terlepas dari ukuran berkas (1 KB hingga 10 MB). Hal
ini mengindikasikan bahwa waktu eksekusi didominasi oleh proses derivasi
kunci (Key Derivation Function), bukan oleh proses enkripsi AES itu sendiri
— temuan ini dibahas lebih lanjut pada bagian 3.

### 2. Analisis Avalanche Effect

Avalanche Effect mengukur seberapa besar perubahan pada cipherteks ketika
terjadi perubahan kecil (misalnya password yang berbeda satu karakter) pada
input. Idealnya, perubahan 1 bit pada kunci/plainteks harus menghasilkan
perubahan sekitar 50% bit pada cipherteks (difusi sempurna).

Hasil pengujian menunjukkan nilai Avalanche Effect berkisar **47,35%–50,04%**,
mendekati nilai ideal 50%. Ini membuktikan bahwa algoritma AES-256-GCM yang
digunakan memiliki sifat difusi yang baik: perubahan sekecil apa pun pada
password/kunci menghasilkan cipherteks yang jauh berbeda dan tidak dapat
diprediksi, sehingga menyulitkan penyerang untuk menganalisis hubungan
antara kunci dan hasil enkripsi.

### 3. Analisis Entropi dan Distribusi Byte (Histogram)

Entropi Shannon mengukur tingkat keacakan data pada skala 0–8 (bit).
Semakin mendekati 8, semakin acak (dan semakin aman) data tersebut.

Hasil pengujian menunjukkan entropi cipherteks meningkat signifikan
dibanding entropi plainteks aslinya, dengan nilai tertinggi **mencapai 8,0**
pada berkas berukuran besar (10 MB) — mendekati batas teoretis maksimum.
Bahkan pada berkas kecil seperti dokumen PDF (66 byte), entropi tetap naik
menjadi 5,83, walau tidak setinggi berkas besar karena ukuran sampel yang
kecil membuat distribusi statistik belum sepenuhnya merata.

Untuk memvisualisasikan hal ini secara lebih konkret, dilakukan pengujian
tambahan menggunakan citra BMP sederhana (lingkaran merah di atas latar
hitam-putih) yang dienkripsi dengan dua pendekatan: **AES mode ECB** dan
**AES-GCM**. Histogram distribusi frekuensi byte (256 bin) hasilnya
ditunjukkan pada `docs/histogram_ecb_vs_gcm.png`:

- **Plainteks asli**: distribusi sangat tidak merata, didominasi dua nilai
  byte ekstrem (0 dan 255) karena gambar hanya berisi warna solid.
- **AES-ECB**: meski nilai byte berubah dari plainteks aslinya, distribusi
  frekuensinya **masih menunjukkan puncak-puncak tajam** (hingga >10.000
  kemunculan pada beberapa byte tertentu). Ini terjadi karena mode ECB
  mengenkripsi setiap blok plainteks yang identik menjadi blok cipherteks
  yang identik pula, sehingga pola berulang pada gambar asli (area warna
  solid) tetap "membayang" pada hasil enkripsi — baik secara statistik
  maupun secara visual (pola lingkaran masih tampak pada gambar terenkripsi).
- **AES-GCM**: distribusi byte **rata di seluruh rentang 0–255** (sekitar
  400–500 kemunculan tiap nilai byte), tanpa puncak mencolok. Ini
  menunjukkan cipherteks AES-GCM secara statistik tidak dapat dibedakan
  dari derau acak (uniform random noise), sehingga tidak membocorkan
  informasi apa pun tentang struktur plainteks aslinya.

Temuan ini menjadi bukti empiris mengapa mode ECB **tidak direkomendasikan**
untuk enkripsi data pada aplikasi nyata, sementara AES-GCM terbukti
menghasilkan output yang aman secara statistik.

### 4. Analisis Dominasi Waktu Key Derivation Function (KDF)

Untuk mengetahui kontribusi masing-masing tahap terhadap total waktu
enkripsi, dilakukan benchmark terpisah antara waktu derivasi kunci
(PBKDF2-HMAC-SHA256, 600.000 iterasi) dan waktu enkripsi AES-GCM murni
(tanpa proses KDF berulang) terhadap data 1 KB:

| Tahap                                    | Waktu Rata-rata (5x pengujian)               |
|------------------------------------------|----------------------------------------------|
| Derivasi kunci (PBKDF2, 600.000 iterasi) | 562,55 ms                                    |
| Enkripsi AES-GCM murni                   | 2,34 ms                                      |
| **Proporsi waktu KDF terhadap total**    | **99,6%**                                    |

Hasil ini mengonfirmasi hipotesis awal: **waktu eksekusi total (Tabel 1)
hampir seluruhnya dihabiskan oleh proses derivasi kunci, bukan oleh
algoritma enkripsi AES itu sendiri.** Ini menjelaskan mengapa waktu
enkripsi pada Tabel 1 relatif konstan (480–680 ms) meskipun ukuran berkas
bervariasi 1.000 kali lipat (1 KB hingga 10 MB) — karena proses yang benar-
benar bergantung pada ukuran data (enkripsi AES) hanya berkontribusi kurang
dari 1% dari total waktu, sedangkan PBKDF2 dengan 600.000 iterasi
menghasilkan waktu komputasi yang tetap besar dan stabil terlepas dari
ukuran data yang dienkripsi.

Jumlah iterasi 600.000 ini sengaja dipilih tinggi (mengikuti rekomendasi
OWASP untuk PBKDF2-HMAC-SHA256) sebagai bentuk pertahanan terhadap serangan
brute-force terhadap password, dengan trade-off berupa waktu proses yang
lebih lambat — sebuah keputusan desain keamanan yang wajar untuk aplikasi
yang mengutamakan perlindungan data sensitif.

### 5. Hasil Pengujian Kualitas Aplikasi (Quality Assurance)

Pengujian fungsional dilakukan terhadap 7 jenis berkas melalui antarmuka
web, meliputi proses enkripsi dan dekripsi penuh (round-trip):

| No | Berkas          | Hasil                                                  |
|----|-----------------|--------------------------------------------------------|
| 1  | sample.pdf      | Berhasil, berkas hasil dekripsi identik dengan aslinya |
| 2  | sample.bmp      | Berhasil, berkas hasil dekripsi identik dengan aslinya |
| 3  | sample.jpg      | Berhasil, berkas hasil dekripsi identik dengan aslinya |
| 4  | sample.png      | Berhasil, berkas hasil dekripsi identik dengan aslinya |
| 5  | sample_1kb.txt  | Berhasil, berkas hasil dekripsi identik dengan aslinya |
| 6  | sample_1mb.txt  | Berhasil, berkas hasil dekripsi identik dengan aslinya |
| 7  | sample_10mb.txt | Berhasil, berkas hasil dekripsi identik dengan aslinya |

Selain pengujian fungsional normal, dilakukan pula dua skenario pengujian
keamanan (negative testing):

| No | Skenario                                                             | Hasil                                         |
|----|----------------------------------------------------------------------|-----------------------------------------------|
| 1  | Password salah saat dekripsi                                         | Ditolak (gagal didekripsi), sesuai ekspektasi |
| 2  | Cipherteks (`.svault`) dimodifikasi secara manual sebelum didekripsi | Ditolak (gagal didekripsi), sesuai ekspektasi |

Kedua hasil negative test ini membuktikan bahwa mode AES-GCM yang
digunakan benar-benar berfungsi sebagai **authenticated encryption**: sistem
tidak hanya mengenkripsi data, tetapi juga mampu mendeteksi apabila
cipherteks telah dimanipulasi atau apabila kunci yang digunakan untuk
dekripsi tidak sesuai, dan menolak untuk menghasilkan output alih-alih
memberikan data yang salah secara diam-diam.



## Referensi

Dworkin, M. J. (2007). *Recommendation for block cipher modes of operation:
Galois/Counter Mode (GCM) and GMAC* (NIST Special Publication 800-38D).
National Institute of Standards and Technology.
https://doi.org/10.6028/NIST.SP.800-38D

Hernandi, R. M. H., & Chandra, J. C. (2024). Implementasi algoritme AES-256
dan AES-GCM untuk mengamankan dokumen pada sistem data rekam medis Klinik
Mulya. *KRESNA: Jurnal Riset dan Pengabdian Masyarakat, 4*(1), 12–22.
https://jurnaldrpm.budiluhur.ac.id/index.php/Kresna/article/view/131

Moriarty, K., Kaliski, B., & Rusch, A. (2017). *PKCS #5: Password-based
cryptography specification version 2.1* (RFC 8018). Internet Engineering
Task Force. https://doi.org/10.17487/RFC8018

Nir, Y., & Langley, A. (2018). *ChaCha20 and Poly1305 for IETF protocols*
(RFC 8439). Internet Engineering Task Force.
https://doi.org/10.17487/RFC8439

Rahman, A. U., Miah, S. U., & Azad, S. (2014). Advanced encryption
standard. Dalam S. Azad & A.-S. K. Pathan (Eds.), *Practical cryptography:
Algorithms and implementations using C++* (hlm. 89–104). CRC Press.

Rahmatulloh, A., Sulastri, H., & Nugroho, R. (2018). Keamanan RESTful web
service menggunakan JSON Web Token (JWT) HMAC SHA-512. *Jurnal Nasional
Teknik Elektro dan Teknologi Informasi, 7*(2), 172–178.
https://doi.org/10.22146/jnteti.v7i2.417

Shannon, C. E. (1948). A mathematical theory of communication. *Bell
System Technical Journal, 27*(3), 379–423.
https://doi.org/10.1002/j.1538-7305.1948.tb01338.x

Stallings, W. (2017). *Cryptography and network security: Principles and
practice* (7th ed.). Pearson Education.

Sönmez Turan, M., Barker, E., Burr, W., & Chen, L. (2010). *Recommendation
for password-based key derivation, part 1: Storage applications* (NIST
Special Publication 800-132). National Institute of Standards and
Technology. https://doi.org/10.6028/NIST.SP.800-132

Zulian, A. P., Kartarina, & Dharma, I. M. Y. (2025). Analisis pengamanan
file menggunakan enkripsi dan dekripsi dengan algoritma AES-GCM-SIV. *Edu
Elektrika Journal, 13*(1), 15–23.
https://doi.org/10.15294/eduel.v13i1.26826