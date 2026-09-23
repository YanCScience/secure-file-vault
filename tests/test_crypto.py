import pytest
from backend.crypto import derive_key, encrypt_file_gcm, decrypt_file_gcm, encrypt_bmp_visual

def test_key_derivation_length():
    """1. Test panjang kunci hasil PBKDF2 harus 256-bit (32 byte)"""
    key = derive_key("password123", b"saltsaltsaltsalt")
    assert len(key) == 32

def test_encryption_decryption_success():
    """2. Test kebenaran dekripsi berkas/teks biasa"""
    data = b"Pesan rahasia ujian kriptografi"
    password = "sandi_kuat_123"
    
    enc_result = encrypt_file_gcm(data, password)
    data_dict = {
        "salt": enc_result["salt"],
        "nonce": enc_result["nonce"],
        "ciphertext": enc_result["ciphertext"],
        "tag": enc_result["tag"]
    }
    decrypted = decrypt_file_gcm(data_dict, password)
    assert decrypted == data

def test_decryption_wrong_password():
    """3. Test penolakan dekripsi jika kata sandi salah"""
    data = b"Data sensitif"
    enc_result = encrypt_file_gcm(data, "sandi_benar")
    
    data_dict = {
        "salt": enc_result["salt"],
        "nonce": enc_result["nonce"],
        "ciphertext": enc_result["ciphertext"],
        "tag": enc_result["tag"]
    }
    with pytest.raises(ValueError):
        decrypt_file_gcm(data_dict, "sandi_salah")

def test_decryption_tampered_ciphertext():
    """4. Test penolakan dekripsi jika 1 byte cipherteks diubah (tamper)"""
    import base64
    data = b"Dokumen PDF Penting"
    enc_result = encrypt_file_gcm(data, "sandi123")
    
    # Ubah 1 byte pada ciphertext
    raw_cipher = bytearray(base64.b64decode(enc_result["ciphertext"]))
    raw_cipher[0] ^= 0xFF # Flip bit byte pertama
    tampered_cipher_b64 = base64.b64encode(bytes(raw_cipher)).decode('utf-8')
    
    data_dict = {
        "salt": enc_result["salt"],
        "nonce": enc_result["nonce"],
        "ciphertext": tampered_cipher_b64,
        "tag": enc_result["tag"]
    }
    with pytest.raises(ValueError):
        decrypt_file_gcm(data_dict, "sandi123")

def test_bmp_header_preservation():
    """5. Test pemisahan 54 byte header BMP tetap utuh setelah enkripsi"""
    dummy_header = b'BM' + b'\x00' * 52
    dummy_pixels = b'\xFF\x00\x00' * 10
    dummy_bmp = dummy_header + dummy_pixels
    
    result = encrypt_bmp_visual(dummy_bmp, "sandi123")
    import base64
    ecb_bmp = base64.b64decode(result["ecb_image_base64"])
    gcm_bmp = base64.b64decode(result["gcm_image_base64"])
    
    assert ecb_bmp[:54] == dummy_header
    assert gcm_bmp[:54] == dummy_header