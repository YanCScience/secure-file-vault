// =========================================================
// script.js
// Logic buat form enkripsi/dekripsi -- manggil API backend
// =========================================================

// ⚠️ PENTING: ganti URL ini sesuai alamat backend Diyani yang SEBENARNYA.
// Ini baru CONTOH/PLACEHOLDER. Tanya endpoint pastinya apa.
const API_ENCRYPT_URL = "/encrypt";
const API_DECRYPT_URL = "/decrypt";

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
    statusLine.textContent = "Menunggu berkas dipilih…";
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
// FUNGSI UTAMA: kirim file + password ke backend
// =========================================================

async function kirimKeBackend(url, aksi) {
  sembunyikanAlert();

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

  tampilkanLoading();
  statusLine.textContent = aksi === "encrypt" ? "Mengunci berkas…" : "Membuka berkas…";

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let pesanError = "Gagal Dekripsi: Kata sandi salah atau berkas telah diubah!";
      try {
        const errorData = await response.json();
        if (errorData.message) pesanError = errorData.message;
      } catch (e) {
        /* respons bukan JSON, pakai pesan default di atas */
      }
      tampilkanAlert(pesanError, "error");
      statusLine.textContent = "Gagal diproses.";
      return;
    }

    const hasil = await response.json();
    outputText.value = hasil.data || JSON.stringify(hasil, null, 2);
    tampilkanAlert("Berhasil diproses!", "success");
    statusLine.textContent = "Selesai.";

  } catch (error) {
    console.error(error);
    tampilkanAlert("Gagal terhubung ke server. Cek koneksi/backend.", "error");
    statusLine.textContent = "Gagal terhubung ke server.";
  } finally {
    sembunyikanLoading();
  }
}


// =========================================================
// EVENT LISTENER: tombol-tombol
// =========================================================

btnEncrypt.addEventListener("click", () => kirimKeBackend(API_ENCRYPT_URL, "encrypt"));
btnDecrypt.addEventListener("click", () => kirimKeBackend(API_DECRYPT_URL, "decrypt"));

btnCopy.addEventListener("click", () => {
  if (!outputText.value) {
    tampilkanAlert("Belum ada hasil buat disalin.", "error");
    return;
  }
  navigator.clipboard.writeText(outputText.value)
    .then(() => tampilkanAlert("Berhasil disalin ke clipboard!", "success"))
    .catch(() => tampilkanAlert("Gagal menyalin ke clipboard.", "error"));
});