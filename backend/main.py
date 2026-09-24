import os
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.crypto import encrypt_data, decrypt_data, encrypt_bmp_ecb
from backend.metrics import calculate_entropy, calculate_byte_histogram

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

app = FastAPI(
    title="Secure File Vault & Crypto Visualizer API",
    version="2.0.0",
    description="Backend API untuk enkripsi data (AAES-GCM / ChaCha20-Poly1305) dan visualisasi mode enkripsi citra."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextEncryptRequest(BaseModel):
    text: str
    password: str
    algorithm: str = "aes-gcm"

class TextDecryptRequest(BaseModel):
    algorithm: str = "aes-gcm"
    salt: str
    nonce: str
    ciphertext: str
    tag: str
    password: str
    iterations:int = 100000

@app.get("/")
def read_root():
    return {"message": "API Secure File Vault Siap", "status": "OK"}

@app.post("/api/encrypt-text")
def api_encrypt_text(payload: TextEncryptRequest):
    try:
        data_bytes = payload.text.encode("utf-8")
        result = encrypt_data(
            data=data_bytes,
            password=payload.password,
            algorithm=payload.algorithm
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/decrypt-text")
def api_decrypt_text(payload: TextDecryptRequest):
    try:
        decrypted_bytes = decrypt_data(payload.model_dump(), payload.password)
        return {"decrypted_text": decrypted_bytes.decode("utf-8")}
    except ValueError:
        raise HTTPException(status_code=400, detail="Kata sandi salah atau data telah diubah (tag verifikasi gagal).")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/encrypt-file")
async def api_encrypt_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    algorithm: str = Form("aes-gcm")
):
    try:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Ukuran berkas melebihi batas 10 MB.")
            
        result = encrypt_data(content, password, algorithm=algorithm)
        result["filename"] = file.filename
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/decrypt-file")
async def api_decrypt_file(
    payload: TextDecryptRequest
):
    try:
        decrypted_bytes = decrypt_data(payload.model_dump(), payload.password)
        return Response(
            content=decrypted_bytes,
            media_type="application/octet-stream"
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Kata sandi salah atau berkas telah terdistorsi/diubah.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/visualize-bmp")
async def api_visualize_bmp(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    try:
        content = await file.read()
        if len(content) < 54 or content[:2] != b'BM':
            raise HTTPException(status_code=400, detail="Berkas harus berformat BMP asli (54-byte header).")
            
        ecb_bytes = encrypt_bmp_ecb(content, password)
        gcm_dict = encrypt_data(content, password, algorithm="aes-gcm")
        
        entropy_plain = calculate_entropy(content)
        entropy_ecb = calculate_entropy(ecb_bytes)
        
        import base64
        gcm_raw = base64.b64decode(gcm_dict["ciphertext"])
        entropy_gcm = calculate_entropy(gcm_raw)
        
        return {
            "entropy": {
                "plain": round(entropy_plain, 4),
                "ecb": round(entropy_ecb, 4),
                "gcm": round(entropy_gcm, 4)
            },
            "ecb_bmp_base64": base64.b64encode(ecb_bytes).decode("utf-8"),
            "gcm_ciphertext_base64": gcm_dict["ciphertext"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))