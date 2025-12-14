import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from ultralytics import YOLO
from PIL import Image
import io
import uvicorn

app = FastAPI(docs_url=None, redoc_url=None)

# --- 1. SETUP KEAMANAN (API KEY) ---
API_KEY_NAME = "x-api-key"
# Pastikan Anda sudah set variable WASTE_API_KEY di Railway
API_KEY = os.environ.get("WASTE_API_KEY")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if API_KEY is None:
        # Jika lupa set key di Railway, server akan error demi keamanan
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: API Key belum dikonfigurasi di Railway."
        )

    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses Ditolak: API Key Salah atau Tidak Ada"
        )

# --- 2. LOAD MODEL ---
try:
    if os.path.exists("best.pt"):
        print("INFO: Menggunakan Model Custom (best.pt)")
        model = YOLO("best.pt")
    else:
        print("INFO: best.pt tidak ditemukan. Menggunakan Model Standar (yolo11n.pt)")
        model = YOLO("yolo11n.pt")
except Exception as e:
    print(f"ERROR: Gagal memuat model. {e}")
    model = None

@app.get("/")
def home():
    return {"message": "Secure Waste API is Running!"}

# --- 3. FUNGSI UTAMA (PREDICT) ---
@app.post("/predict", dependencies=[Security(get_api_key)])
async def predict(file: UploadFile = File(...)):
    if model is None:
        return {"error": "Model AI belum siap."}

    # BAGIAN INI YANG HILANG DI KODE ANDA SEBELUMNYA:
    try:
        # 1. Baca data gambar yang dikirim
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # 2. Suruh AI memproses gambar
        results = model(image, conf=0.25)

        # 3. Cek hasil deteksi
        if len(results) > 0 and len(results[0].boxes) > 0:
            box = results[0].boxes[0]

            class_id = int(box.cls)
            class_name = model.names[class_id]
            confidence = float(box.conf)

            return {
                "class": class_name,
                "confidence": confidence,
                "message": "Objek ditemukan"
            }
        else:
            return {
                "class": "Tidak Diketahui",
                "confidence": 0.0,
                "message": "Tidak ada objek yang dikenali"
            }

    except Exception as e:
        return {"error": f"Gagal memproses gambar: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)