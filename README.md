# Exercise Repetition Counter dengan Pose Detection

Aplikasi berbasis Python yang dapat menghitung jumlah repetisi latihan (push-up atau squat) secara otomatis menggunakan deteksi pose tubuh dari MediaPipe Pose dengan antarmuka pengguna grafis (GUI) yang intuitif.

## 🚀 Fitur Utama

- **Deteksi Pose Real-time**: Menggunakan MediaPipe untuk mendeteksi 33 titik tubuh (keypoints)
- **Penghitungan Otomatis**: Menghitung repetisi push-up dan squat berdasarkan sudut sendi
- **GUI Intuitif**: Antarmuka pengguna yang mudah digunakan dengan Tkinter
- **Statistik Sesi**: Melacak durasi, jumlah repetisi, dan waktu latihan
- **Export Data**: Menyimpan data statistik ke file CSV
- **Validasi Gerakan**: State machine untuk memastikan akurasi penghitungan

## 📋 Persyaratan Sistem

- Python 3.8 atau lebih baru
- Webcam yang berfungsi (resolusi minimal 640x480)
- CPU dengan kemampuan pemrosesan real-time
- RAM minimal 4GB
- Windows/Linux/macOS

## 🛠️ Instalasi

### 1. Clone atau Download Project
```bash
# Download semua file ke folder lokal Anda
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
python exercise_counter.py
```

## 📖 Panduan Penggunaan

### Memulai Aplikasi
1. Jalankan `exercise_counter.py`
2. Pastikan webcam terhubung dan berfungsi
3. Pilih jenis latihan (Push-Up atau Squat) dari dropdown
4. Klik tombol "Start" untuk memulai sesi

### Melakukan Latihan

#### Push-Up:
- Posisikan tubuh dalam posisi push-up di depan kamera
- Pastikan bahu, siku, dan pergelangan tangan terlihat jelas
- Lakukan gerakan push-up dengan range penuh
- Aplikasi akan menghitung repetisi berdasarkan sudut siku:
  - **DOWN**: Sudut siku < 90°
  - **UP**: Sudut siku > 160°

#### Squat:
- Berdiri tegak di depan kamera
- Pastikan pinggul, lutut, dan pergelangan kaki terlihat
- Lakukan gerakan squat dengan range penuh
- Aplikasi akan menghitung repetisi berdasarkan sudut lutut:
  - **DOWN**: Sudut lutut < 100°
  - **UP**: Sudut lutut > 170°

### Kontrol Aplikasi
- **Start**: Memulai sesi latihan dan aktivasi kamera
- **Stop**: Menghentikan sesi dan menyimpan data
- **Reset**: Mengatur ulang counter dan statistik
- **Export Data**: Menyimpan data sesi ke file CSV

### Panel Statistik
- **Repetitions**: Jumlah repetisi yang berhasil dihitung
- **Duration**: Durasi sesi latihan (menit:detik)
- **Start Time**: Waktu mulai sesi
- **Status**: Indikator fase gerakan (UP/DOWN/READY)

## 📊 Format Data Export

Data sesi akan disimpan dalam format CSV dengan kolom:
- `date_time`: Tanggal dan waktu sesi
- `exercise_type`: Jenis latihan (Push-Up/Squat)
- `repetitions`: Jumlah repetisi
- `duration_seconds`: Durasi dalam detik
- `duration_formatted`: Durasi dalam format MM:SS

Contoh file: `exercise_data_20241225_143022.csv`

## 🔧 Konfigurasi dan Optimasi

### Pengaturan MediaPipe
```python
# Dalam kode, Anda dapat menyesuaikan confidence threshold:
self.pose = self.mp_pose.Pose(
    min_detection_confidence=0.5,  # Tingkatkan untuk akurasi lebih tinggi
    min_tracking_confidence=0.5    # Tingkatkan untuk tracking yang lebih stabil
)
```

### Threshold Sudut
Anda dapat menyesuaikan threshold sudut dalam fungsi `detect_push_up()` dan `detect_squat()`:
- Push-up: DOWN < 90°, UP > 160°
- Squat: DOWN < 100°, UP > 170°

## 🚨 Troubleshooting

### Kamera Tidak Terdeteksi
- Pastikan webcam terhubung dan tidak digunakan aplikasi lain
- Coba restart aplikasi
- Periksa permission kamera di sistem operasi

### Pose Tidak Terdeteksi
- Pastikan pencahayaan cukup
- Posisikan tubuh dalam frame kamera
- Hindari background yang terlalu ramai
- Gunakan pakaian yang kontras dengan background

### Penghitungan Tidak Akurat
- Lakukan gerakan dengan range penuh
- Pastikan landmark kunci terlihat jelas
- Hindari gerakan terlalu cepat
- Kalibrasi posisi awal sebelum memulai

### Performance Issues
- Tutup aplikasi lain yang menggunakan kamera
- Kurangi resolusi kamera jika diperlukan
- Pastikan CPU tidak overload

## 🎯 Tips Penggunaan Optimal

1. **Pencahayaan**: Gunakan pencahayaan yang cukup dan merata
2. **Background**: Pilih background yang sederhana dan kontras
3. **Posisi**: Posisikan tubuh sepenuhnya dalam frame kamera
4. **Pakaian**: Gunakan pakaian yang kontras dengan background
5. **Gerakan**: Lakukan gerakan dengan tempo yang konsisten
6. **Kalibrasi**: Reset counter sebelum memulai sesi baru

## 📝 Struktur File

```
exercise_counter/
├── exercise_counter.py    # File utama aplikasi
├── requirements.txt       # Dependencies Python
├── README.md             # Dokumentasi ini
└── exercise_data_*.csv   # File export data (dibuat otomatis)
```

## 🔄 Update dan Pengembangan

Untuk pengembangan lebih lanjut, Anda dapat:
- Menambah jenis latihan baru
- Implementasi deteksi postur yang lebih kompleks
- Menambah fitur analisis form latihan
- Integrasi dengan database
- Menambah fitur pelaporan yang lebih detail

## 📞 Support

Jika mengalami masalah atau memiliki pertanyaan:
1. Periksa bagian Troubleshooting di atas
2. Pastikan semua dependencies terinstall dengan benar
3. Verifikasi kompatibilitas sistem dan hardware

---

**Selamat berlatih! 💪**