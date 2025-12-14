# Gunakan Python 3.11 Slim (Versi stabil dan ringan)
FROM python:3.11-slim

# 1. INSTALL SYSTEM LIBRARY YANG HILANG (KUNCI PERBAIKAN)
# Kita install libgl1 dan libglib2.0 secara manual lewat apt-get
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Folder Kerja
WORKDIR /app

# 3. Copy Requirements
COPY requirements.txt .

# 4. Install Python Dependencies
# Kita install pip versi terbaru dulu agar stabil
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Semua Source Code
COPY . .

# 6. Jalankan Aplikasi
# Menggunakan variabel PORT dari Railway
CMD uvicorn main:app --host 0.0.0.0 --port $PORT