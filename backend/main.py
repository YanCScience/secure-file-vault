from fastapi import FastAPI

app = FastAPI(title="Aplikasi Kriptografi - Enkripsi Citra")

@app.get("/")
def read_root():
    return {"status": "Backend Kriptografi Siap"}