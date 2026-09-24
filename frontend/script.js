// =========================================================
// script.js
// Logic buat form enkripsi/dekripsi -- manggil API backend
// =========================================================
//
// PENJELASAN ALUR:
// -----------------
// ENKRIPSI:
//   1. User pilih file asli + isi password
//   2. Dikirim ke POST /api/encrypt-file (multipart: file, password, algorithm)
//   3. Backend balikin JSON: { algorithm, salt, nonce, ciphertext, tag, iterations, filename }
//      (semua field selain "filename" & "iterations" itu base64 text)
//   4. JSON itu kita BUNGKUS jadi satu file teks ".svault" dan otomatis di-download.
//      Ini "amplop" yang isinya semua info buat dekripsi ulang nanti (KECUALI
//      password -- password TIDAK disimpan di file ini demi keamanan).
//
// DEKRIPSI:
//   1. User upload file ".svault" (hasil dari proses Enkripsi tadi) + isi password
//   2. File .svault itu isinya teks JSON -> kita baca & parse di browser
//   3. Kita kirim sebagai JSON body ke POST /api/decrypt-file
//      (bukan multipart, backend memang minta format JSON polos untuk endpoint ini)
//   4. Kalau password benar & data tidak diubah -> backend balikin ISI FILE ASLI
//      (bytes mentah, bukan JSON) -> otomatis di-download dengan nama file aslinya
//   5. Kalau password salah / data diutak-atik -> backend menolak (auth tag GCM gagal)
//
// =========================================================

const API_BASE_URL = "http://localhost:8000";
const API_ENCRYPT_URL = API_BASE_URL + "/api/encrypt-file";
const API_DECRYPT_URL = API_BASE_URL + "/api/decrypt-file";
const ALGORITMA_DEFAULT = "aes-gcm"; // pilihan lain: "chacha20-poly1305"

// Ambil semua elemen HTML yang kepake
const dropzone = document.getElementById("dropzone");
const dropzoneLabel = document.getElementById("dropzoneLabel");
const fileInput = document.getElementById("fileInput");
const passwordInput = document.getElementById("passwordInput");
const btnTogglePw = document.getElementById("btnTogglePw");
const btnEncrypt = document.getElementById("btnEncrypt");
const btnDecrypt = document.getElementById("btnDecrypt");
const btnCopy = document.getElementById("btnCopy");
const outputText = document.getElementById("outputText");
const alertBox = document.getElementById("alertBox");
const loadingIndicator = document.getElementById("loadingIndicator");
const statusLine = document.getElementById("statusLine");
const downloadLink = document.getElementById("downloadLink");


// =========================================================
// FUNGSI BANTUAN: alert & loading
// =========================================================

function tampilkanAlert(pesan, jenis) {
  alertBox.textContent = pesan;
  alertBox.className = "alert alert-" + jenis;
}

function sembunyikanAlert() {
  alertBox.className = "alert hidden";
}

function tampilkanLoading() {
  loadingIndicator.classList.remove("hidden");
  btnEncrypt.disabled = true;
  btnDecrypt.disabled = true;
}

function sembunyikanLoading() {
  loadingIndicator.classList.add("hidden");
  btnEncrypt.disabled = false;
  btnDecrypt.disabled = false;
}

function sembunyikanTombolDownload() {
  downloadLink.classList.add("hidden");
  if (downloadLink.href) {
    URL.revokeObjectURL(downloadLink.href);
    downloadLink.removeAttribute("href");
  }
}

// Bikin tombol download muncul, mengarah ke sebuah Blob (file di memory browser)
function siapkanTombolDownload(namaFile, blob) {
  sembunyikanTombolDownload(); // buang link lama kalau ada, biar gak numpuk di memory
  const url = URL.createObjectURL(blob);
  downloadLink.href = url;
  downloadLink.download = namaFile;
  downloadLink.textContent = "\u2193 Unduh " + namaFile;
  downloadLink.classList.remove("hidden");
}


// =========================================================
// DROPZONE: klik buat buka file picker + drag & drop
// =========================================================

fileInput.addEventListener("change", () => {
  perbaruiLabelFile();
});

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("is-dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("is-dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("is-dragover");
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    perbaruiLabelFile();
  }
});

function perbaruiLabelFile() {
  const file = fileInput.files[0];
  if (file) {
    dropzoneLabel.textContent = file.name;
    statusLine.textContent = `Siap: ${file.name} (${formatUkuran(file.size)})`;
  } else {
    dropzoneLabel.textContent = "Klik atau seret berkas ke sini";
    statusLine.textContent = "Menunggu berkas dipilih\u2026";
  }
}

function formatUkuran(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}


// =========================================================
// TOGGLE LIHAT/SEMBUNYIKAN KATA SANDI
// =========================================================

btnTogglePw.addEventListener("click", () => {
  const sedangDitampilkan = passwordInput.type === "text";
  passwordInput.type = sedangDitampilkan ? "password" : "text";
  btnTogglePw.setAttribute(
    "aria-label",
    sedangDitampilkan ? "Tampilkan kata sandi" : "Sembunyikan kata sandi"
  );
});


// =========================================================
// FUNGSI BANTUAN: baca pesan error dari backend (FastAPI)
// =========================================================
// FastAPI selalu balikin error dalam bentuk { "detail": "..." }
// -- BUKAN { "message": "..." } seperti dugaan awal.
async function bacaPesanError(response, pesanFallback) {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
  } catch (e) {
    /* respons bukan JSON, pakai fallback di bawah */
  }
  return pesanFallback;
}


// =========================================================
// ALUR 1: ENKRIPSI -- file asli masuk, file .svault keluar
// =========================================================

async function prosesEnkripsi() {
  sembunyikanAlert();
  sembunyikanTombolDownload();

  const file = fileInput.files[0];
  const password = passwordInput.value;

  if (!file) {
    tampilkanAlert("Pilih berkas dulu ya sebelum lanjut!", "error");
    return;
  }
  if (!password) {
    tampilkanAlert("Kata sandi belum diisi!", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("password", password);
  formData.append("algorithm", ALGORITMA_DEFAULT);

  tampilkanLoading();
  statusLine.textContent = "Mengunci berkas\u2026";

  try {
    const response = await fetch(API_ENCRYPT_URL, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const pesan = await bacaPesanError(response, "Gagal mengunci berkas.");
      tampilkanAlert(pesan, "error");
      statusLine.textContent = "Gagal diproses.";
      return;
    }

    // hasil = { algorithm, salt, nonce, ciphertext, tag, iterations, filename }
    const hasil = await response.json();

    // Tampilkan cuplikan cipherteks di kotak "Hasil" (biar keliatan, sesuai requirement soal)
    outputText.value = hasil.ciphertext;

    // Bungkus SEMUA info (kecuali password) jadi file .svault yang bisa di-download
    const namaFileVault = hasil.filename + ".svault";
    const isiVault = JSON.stringify(hasil, null, 2);
    const blob = new Blob([isiVault], { type: "application/json" });
    siapkanTombolDownload(namaFileVault, blob);

    tampilkanAlert(
      "Berhasil dikunci! Klik \u201cUnduh hasil\u201d untuk menyimpan berkas .svault.",
      "success"
    );
    statusLine.textContent = "Selesai. Berkas .svault siap diunduh.";

  } catch (error) {
    console.error(error);
    tampilkanAlert("Gagal terhubung ke server. Pastikan backend (uvicorn) sedang berjalan.", "error");
    statusLine.textContent = "Gagal terhubung ke server.";
  } finally {
    sembunyikanLoading();
  }
}


// =========================================================
// ALUR 2: DEKRIPSI -- file .svault masuk, file asli keluar
// =========================================================

async function prosesDekripsi() {
  sembunyikanAlert();
  sembunyikanTombolDownload();

  const file = fileInput.files[0];
  const password = passwordInput.value;

  if (!file) {
    tampilkanAlert("Pilih berkas .svault dulu ya sebelum lanjut!", "error");
    return;
  }
  if (!password) {
    tampilkanAlert("Kata sandi belum diisi!", "error");
    return;
  }

  tampilkanLoading();
  statusLine.textContent = "Membaca berkas .svault\u2026";

  try {
    // --- baca isi file .svault (teks JSON) dan parse ---
    let vault;
    try {
      const teksVault = await file.text();
      vault = JSON.parse(teksVault);
    } catch (e) {
      tampilkanAlert("Berkas .svault tidak valid atau rusak (bukan JSON yang benar).", "error");
      statusLine.textContent = "Berkas tidak valid.";
      return;
    }

    // --- susun payload JSON persis sesuai yang diminta backend ---
    const payload = {
      algorithm: vault.algorithm,
      salt: vault.salt,
      nonce: vault.nonce,
      ciphertext: vault.ciphertext,
      tag: vault.tag,
      password: password,
      iterations: vault.iterations,
    };

    statusLine.textContent = "Membuka berkas\u2026";
    const response = await fetch(API_DECRYPT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      // Backend sudah kasih pesan yang enak dibaca untuk kasus ini, contoh:
      // "Kata sandi salah atau berkas telah terdistorsi/diubah."
      const pesan = await bacaPesanError(
        response,
        "Gagal Dekripsi: Kata sandi salah atau berkas telah diubah!"
      );
      tampilkanAlert(pesan, "error");
      statusLine.textContent = "Gagal diproses.";
      return;
    }

    // Respons sukses = bytes mentah file asli (bukan JSON)
    const blob = await response.blob();
    const namaFileAsli = vault.filename || "berkas_hasil_dekripsi";
    siapkanTombolDownload(namaFileAsli, blob);

    outputText.value = `Berkas "${namaFileAsli}" berhasil didekripsi (${formatUkuran(blob.size)}).`;
    tampilkanAlert(
      "Berhasil dibuka! Klik \u201cUnduh hasil\u201d untuk menyimpan berkas asli.",
      "success"
    );
    statusLine.textContent = "Selesai. Berkas asli siap diunduh.";

  } catch (error) {
    console.error(error);
    tampilkanAlert("Gagal terhubung ke server. Pastikan backend (uvicorn) sedang berjalan.", "error");
    statusLine.textContent = "Gagal terhubung ke server.";
  } finally {
    sembunyikanLoading();
  }
}


// =========================================================
// EVENT LISTENER: tombol-tombol
// =========================================================

btnEncrypt.addEventListener("click", prosesEnkripsi);
btnDecrypt.addEventListener("click", prosesDekripsi);

btnCopy.addEventListener("click", () => {
  if (!outputText.value) {
    tampilkanAlert("Belum ada hasil buat disalin.", "error");
    return;
  }
  navigator.clipboard.writeText(outputText.value)
    .then(() => tampilkanAlert("Berhasil disalin ke clipboard!", "success"))
    .catch(() => tampilkanAlert("Gagal menyalin ke clipboard.", "error"));
});


// =========================================================
// LANGKAH 3: IMAGE CRYPTO VISUALIZATION (Original vs ECB vs GCM)
//
// Endpoint backend (backend/main.py):
//   POST {API_BASE_URL}/api/visualize-bmp   (multipart: file, password)
// Response backend yang sebenarnya:
//   {
//     "entropy": { "plain": n, "ecb": n, "gcm": n },
//     "ecb_bmp_base64": "...",          // BMP utuh (header 54 byte asli + piksel ECB)
//     "gcm_ciphertext_base64": "..."    // ciphertext mentah GCM, TANPA header BMP
//   }
// Backend hanya menerima BMP 24-bit dengan header 54 byte, jadi gambar apa pun
// (PNG/JPG/GIF/WebP/BMP) dikonversi dulu ke BMP 24-bit di browser lewat <canvas>.
// Ciphertext GCM tidak punya header BMP, jadi 54 byte pertamanya diganti dengan
// header BMP asli supaya browser mau menampilkannya sebagai gambar.
// =========================================================
(function () {
  // Backend belum menyajikan file frontend, jadi alamat API harus absolut.
  // Ubah kalau backend jalan di host/port lain.
  const API_BASE_URL = "http://localhost:8000";
  const API_VISUALIZE_URL = API_BASE_URL + "/api/visualize-bmp";

  const BMP_HEADER_SIZE = 54;
  const MAX_SIDE = 512; // sisi terpanjang gambar dibatasi supaya proses cepat

  const imgFileInput = document.getElementById("imgFileInput");
  const imgDropzone = document.getElementById("imgDropzone");
  const imgDropzoneLabel = document.getElementById("imgDropzoneLabel");
  const imgPasswordInput = document.getElementById("imgPasswordInput");
  const btnToggleImgPw = document.getElementById("btnToggleImgPw");
  const btnCompareImage = document.getElementById("btnCompareImage");
  const imgAlert = document.getElementById("imgAlert");
  const imgStatusLine = document.getElementById("imgStatusLine");

  const panels = {
    original: { img: document.getElementById("imgOriginal"), frame: document.getElementById("frameOriginal"), meta: document.getElementById("metaOriginal") },
    ecb: { img: document.getElementById("imgEcb"), frame: document.getElementById("frameEcb"), meta: document.getElementById("metaEcb") },
    gcm: { img: document.getElementById("imgGcm"), frame: document.getElementById("frameGcm"), meta: document.getElementById("metaGcm") },
  };

  let objectUrls = []; // blob URL aktif, di-revoke sebelum render ulang

  // ---------- alert & status (gaya sama dengan alert utama) ----------
  function tampilkanAlertGambar(pesan, jenis) {
    imgAlert.textContent = pesan;
    imgAlert.className = "alert alert-" + jenis;
  }

  function sembunyikanAlertGambar() {
    imgAlert.className = "alert hidden";
  }

  function setBusy(busy) {
    btnCompareImage.disabled = busy;
  }

  // ---------- dropzone & toggle password ----------
  function perbaruiLabelGambar() {
    const file = imgFileInput.files[0];
    if (file) {
      imgDropzoneLabel.textContent = file.name;
      imgStatusLine.textContent = `Siap: ${file.name} (${formatUkuran(file.size)})`;
    } else {
      imgDropzoneLabel.textContent = "Klik atau seret gambar ke sini";
      imgStatusLine.textContent = "Menunggu gambar dipilih…";
    }
  }

  imgFileInput.addEventListener("change", perbaruiLabelGambar);
  imgDropzone.addEventListener("dragover", (e) => { e.preventDefault(); imgDropzone.classList.add("is-dragover"); });
  imgDropzone.addEventListener("dragleave", () => imgDropzone.classList.remove("is-dragover"));
  imgDropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    imgDropzone.classList.remove("is-dragover");
    if (e.dataTransfer.files.length > 0) {
      imgFileInput.files = e.dataTransfer.files;
      perbaruiLabelGambar();
    }
  });

  btnToggleImgPw.addEventListener("click", () => {
    const tampil = imgPasswordInput.type === "text";
    imgPasswordInput.type = tampil ? "password" : "text";
    btnToggleImgPw.setAttribute("aria-label", tampil ? "Tampilkan kata sandi" : "Sembunyikan kata sandi");
  });

  // ---------- konversi gambar -> BMP 24-bit (header 54 byte) ----------
  function muatGambar(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        if (!img.naturalWidth || !img.naturalHeight) {
          reject(new Error("Gambar tidak memiliki ukuran yang valid."));
        } else {
          resolve(img);
        }
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error("Berkas tidak bisa dibaca sebagai gambar. Coba PNG, JPG, BMP, GIF, atau WebP."));
      };
      img.src = url;
    });
  }

  function gambarKeBmp24(img) {
    const skala = Math.min(1, MAX_SIDE / Math.max(img.naturalWidth, img.naturalHeight));
    const w = Math.max(1, Math.round(img.naturalWidth * skala));
    const h = Math.max(1, Math.round(img.naturalHeight * skala));

    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff"; // BMP 24-bit tidak punya alpha
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0, w, h);
    const rgba = ctx.getImageData(0, 0, w, h).data;

    const stride = (w * 3 + 3) & ~3; // tiap baris BMP dipadatkan ke kelipatan 4 byte
    const ukuranPiksel = stride * h;
    const buf = new ArrayBuffer(BMP_HEADER_SIZE + ukuranPiksel);
    const view = new DataView(buf);
    const bytes = new Uint8Array(buf);

    bytes[0] = 0x42; bytes[1] = 0x4d;              // "BM"
    view.setUint32(2, buf.byteLength, true);       // ukuran file
    view.setUint32(10, BMP_HEADER_SIZE, true);     // offset data piksel
    view.setUint32(14, 40, true);                  // ukuran BITMAPINFOHEADER
    view.setInt32(18, w, true);
    view.setInt32(22, h, true);                    // positif = baris dari bawah ke atas
    view.setUint16(26, 1, true);                   // planes
    view.setUint16(28, 24, true);                  // bit per piksel
    view.setUint32(34, ukuranPiksel, true);
    view.setInt32(38, 2835, true);
    view.setInt32(42, 2835, true);

    for (let y = 0; y < h; y++) {
      const barisTujuan = BMP_HEADER_SIZE + (h - 1 - y) * stride;
      for (let x = 0; x < w; x++) {
        const src = (y * w + x) * 4;
        const dst = barisTujuan + x * 3;
        bytes[dst] = rgba[src + 2];     // B
        bytes[dst + 1] = rgba[src + 1]; // G
        bytes[dst + 2] = rgba[src];     // R
      }
    }
    return { bytes, width: w, height: h };
  }

  // ---------- helper base64 & render ----------
  function base64KeBytes(b64) {
    const bin = atob(b64); // melempar error kalau base64 tidak valid
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }

  function bacaAngka(n) {
    return typeof n === "number" && isFinite(n) ? n.toFixed(4) : "-";
  }

  function validasiRespons(hasil, bmpAsli) {
    if (!hasil || typeof hasil.ecb_bmp_base64 !== "string" || typeof hasil.gcm_ciphertext_base64 !== "string") {
      throw new Error("field ecb_bmp_base64 / gcm_ciphertext_base64 tidak ditemukan.");
    }
    let ecb, gcmMentah;
    try {
      ecb = base64KeBytes(hasil.ecb_bmp_base64);
      gcmMentah = base64KeBytes(hasil.gcm_ciphertext_base64);
    } catch (e) {
      throw new Error("data base64 tidak valid.");
    }
    if (ecb.length !== bmpAsli.length || gcmMentah.length !== bmpAsli.length) {
      throw new Error("ukuran hasil enkripsi tidak sama dengan ukuran gambar yang dikirim.");
    }
    if (ecb[0] !== 0x42 || ecb[1] !== 0x4d) {
      throw new Error("hasil ECB bukan BMP yang valid.");
    }
    // Ciphertext GCM menutupi seluruh berkas (termasuk header), jadi pasang lagi header asli.
    const gcmBmp = new Uint8Array(gcmMentah);
    gcmBmp.set(bmpAsli.subarray(0, BMP_HEADER_SIZE), 0);
    return { ecb, gcmBmp, entropy: hasil.entropy || {} };
  }

  function bersihkanPanel(p) {
    p.frame.classList.remove("has-image");
    p.img.removeAttribute("src");
    p.meta.innerHTML = "&nbsp;";
  }

  function resetHasil() {
    objectUrls.forEach((u) => URL.revokeObjectURL(u));
    objectUrls = [];
    Object.values(panels).forEach(bersihkanPanel);
  }

  function renderKePanel(panel, bytes, keterangan) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(new Blob([bytes], { type: "image/bmp" }));
      objectUrls.push(url);
      panel.img.onload = () => {
        panel.frame.classList.add("has-image");
        panel.meta.textContent = keterangan;
        resolve();
      };
      panel.img.onerror = () => reject(new Error("Gambar gagal ditampilkan oleh browser."));
      panel.img.src = url;
    });
  }

  async function bacaPesanError(response) {
    try {
      const data = await response.json();
      if (typeof data.detail === "string") return "Backend menolak permintaan: " + data.detail;
      if (Array.isArray(data.detail)) return "Data yang dikirim ke backend tidak lengkap atau tidak valid.";
    } catch (e) { /* bukan JSON */ }
    return `Backend error (HTTP ${response.status}).`;
  }

  // ---------- alur utama ----------
  async function bandingkanGambar() {
    sembunyikanAlertGambar();

    const file = imgFileInput.files[0];
    const password = imgPasswordInput.value;

    if (!file) {
      tampilkanAlertGambar("Pilih gambar dulu ya sebelum lanjut!", "error");
      return;
    }
    if (!file.type.startsWith("image/")) {
      tampilkanAlertGambar("Berkas yang dipilih bukan gambar. Pilih PNG, JPG, BMP, GIF, atau WebP.", "error");
      return;
    }
    if (!password) {
      tampilkanAlertGambar("Kata sandi belum diisi!", "error");
      return;
    }

    setBusy(true);
    resetHasil();

    try {
      imgStatusLine.textContent = "Menyiapkan gambar…";
      let bmp;
      try {
        bmp = gambarKeBmp24(await muatGambar(file));
      } catch (e) {
        tampilkanAlertGambar(e.message, "error");
        imgStatusLine.textContent = "Gagal menyiapkan gambar.";
        return;
      }

      imgStatusLine.textContent = "Mengirim ke backend dan mengenkripsi…";
      const formData = new FormData();
      formData.append("file", new File([bmp.bytes], "image.bmp", { type: "image/bmp" }));
      formData.append("password", password);

      let response;
      try {
        response = await fetch(API_VISUALIZE_URL, { method: "POST", body: formData });
      } catch (e) {
        console.error(e);
        tampilkanAlertGambar(`Gagal terhubung ke backend (${API_BASE_URL}). Pastikan uvicorn sudah berjalan.`, "error");
        imgStatusLine.textContent = "Gagal terhubung ke server.";
        return;
      }

      if (!response.ok) {
        tampilkanAlertGambar("Enkripsi gagal. " + (await bacaPesanError(response)), "error");
        imgStatusLine.textContent = "Gagal diproses.";
        return;
      }

      let hasil;
      try {
        hasil = await response.json();
      } catch (e) {
        tampilkanAlertGambar("Respons backend bukan JSON yang valid.", "error");
        imgStatusLine.textContent = "Respons tidak valid.";
        return;
      }

      let data;
      try {
        data = validasiRespons(hasil, bmp.bytes);
      } catch (e) {
        tampilkanAlertGambar("Respons backend tidak valid: " + e.message, "error");
        imgStatusLine.textContent = "Respons tidak valid.";
        return;
      }

      const ukuran = `${bmp.width}×${bmp.height} px`;
      try {
        await renderKePanel(panels.original, bmp.bytes, `${ukuran} · entropi ${bacaAngka(data.entropy.plain)} / 8`);
        await renderKePanel(panels.ecb, data.ecb, `${ukuran} · entropi ${bacaAngka(data.entropy.ecb)} / 8`);
        await renderKePanel(panels.gcm, data.gcmBmp, `${ukuran} · entropi ${bacaAngka(data.entropy.gcm)} / 8`);
      } catch (e) {
        tampilkanAlertGambar(e.message, "error");
        imgStatusLine.textContent = "Gagal menampilkan gambar.";
        return;
      }

      tampilkanAlertGambar("Berhasil! Bandingkan pola pada AES-ECB dengan noise pada AES-GCM.", "success");
      imgStatusLine.textContent = "Selesai.";
    } finally {
      setBusy(false);
    }
  }

  btnCompareImage.addEventListener("click", bandingkanGambar);
})();