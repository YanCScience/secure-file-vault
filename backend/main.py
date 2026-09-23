from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import crypto

app = FastAPI(title="Secure File Vault & Citra Visualizer API")

# Izinkan CORS agar Frontend Agniya bisa mengakses API dari port berbeda
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DecryptRequest(BaseModel):
    salt: str
    nonce: str
    ciphertext: str
    tag: str
    password: str

@app.get("/")
def read_root():
    return {"status": "Backend Kriptografi Siap"}

@app.post("/api/encrypt-file")
async def encrypt_file_endpoint(file: UploadFile = File(...), password: str = Form(...)):
    """Endpoint untuk mengenkripsi berkas umum (PDF, Teks, dll)."""
    try:
        content = await file.read()
        result = crypto.encrypt_file_gcm(content, password)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/decrypt-file")
def decrypt_file_endpoint(req: DecryptRequest):
    """Endpoint dekripsi berkas. Akan menolak jika sandi salah / data diubah."""
    try:
        data_dict = req.dict()
        password = data_dict.pop("password")
        decrypted_bytes = crypto.decrypt_file_gcm(data_dict, password)
        return {
            "status": "success", 
            "decrypted_content_base64": crypto.base64.b64encode(decrypted_bytes).decode('utf-8')
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Gagal Dekripsi: Kata sandi salah atau data telah diubah!")

@app.post("/api/visualize-bmp")
async def visualize_bmp_endpoint(file: UploadFile = File(...), password: str = Form(...)):
    """Endpoint khusus visualisasi enkripsi gambar BMP (ECB vs GCM)."""
    try:
        content = await file.read()
        result = crypto.encrypt_bmp_visual(content, password)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal memproses gambar BMP: {str(e)}")