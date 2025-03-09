# YouTube Video Downloader & Processor

## 📌 Deskripsi

Skrip ini memungkinkan Anda untuk mengunduh video dari YouTube dengan berbagai pilihan resolusi, mengekstrak audio, mengompresi video, serta membagi video menjadi beberapa bagian dengan bantuan GPU NVIDIA (NVENC) untuk performa optimal.

## 🔥 Fitur Utama

1. **Mengunduh Video dari YouTube**: Bisa memilih resolusi yang tersedia (MP4 dengan codec AVC1, VP9, AV1).
2. **Menampilkan Format Video dengan Audio**: Memastikan video yang diunduh memiliki audio.
3. **Mengekstrak Audio**: Mengambil audio dari video menggunakan FFmpeg.
4. **Menggabungkan Video dan Audio**: Jika format video yang dipilih tidak memiliki audio, bisa digabungkan dengan audio terpisah.
5. **Mengompresi Video**: Mengurangi ukuran file video dengan tetap mempertahankan kualitas optimal menggunakan GPU NVIDIA (NVENC) atau CPU (libx265).
6. **Membagi Video**: Memotong video menjadi beberapa bagian dengan durasi yang ditentukan serta menambahkan teks overlay.

## 🖥️ Spesifikasi Minimum

- **OS**: Windows 10/11, Linux, macOS
- **CPU**: Intel Core i5 / AMD Ryzen 5 atau lebih tinggi
- **GPU (Opsional)**: NVIDIA dengan dukungan NVENC untuk kompresi video lebih cepat
- **RAM**: Minimal 8GB (Direkomendasikan 16GB untuk pemrosesan lebih cepat)
- **Penyimpanan**: Minimal 10GB kosong (tergantung pada ukuran video yang diunduh)
- **Software Tambahan**:
  - Python 3.8 atau lebih baru
  - FFmpeg dengan dukungan NVENC
  - yt-dlp (untuk pengunduhan video dari YouTube)

## 📦 Requirement

Skrip ini membutuhkan dependensi berikut:

- Python 3.8+
- yt-dlp
- FFmpeg
- subprocess
- os
- sys
- re

### 📄 `requirements.txt`

Berikut daftar dependensi yang perlu diinstal:

```
yt-dlp
ffmpeg-python
```

Untuk menginstalnya, jalankan perintah berikut:

```sh
pip install -r requirements.txt
```

## 🛠️ Instalasi

### 1. **Install Python**

Unduh dan install Python dari [python.org](https://www.python.org/downloads/). Pastikan Anda mencentang opsi **Add Python to PATH** saat instalasi.

### 2. **Install Dependensi**

Jalankan perintah berikut untuk menginstal dependensi yang diperlukan:

```sh
pip install yt-dlp
```

### 3. **Install FFmpeg**

- **Windows**:

  1. Unduh **FFmpeg** dari [ffmpeg.org](https://ffmpeg.org/download.html).
  2. Ekstrak ke `C:\ffmpeg\bin`.
  3. Tambahkan `C:\ffmpeg\bin` ke **Environment Variables** → **Path**.

- **Linux (Ubuntu/Debian)**:

```sh
sudo apt update && sudo apt install ffmpeg -y
```

- **MacOS (Homebrew)**:

```sh
brew install ffmpeg
```

### 4. **Jalankan Skrip**

Setelah semua dependensi terinstal, jalankan skrip dengan perintah berikut:

```sh
python script.py
```

## 🚀 Cara Penggunaan

1. **Masukkan URL YouTube**
2. **Pilih resolusi video** yang tersedia
3. **Pilih format audio** jika ingin mengekstrak atau menggabungkan audio
4. **Tentukan path penyimpanan output**
5. **Otomatis mengunduh, mengekstrak audio, menggabungkan, mengompresi, dan membagi video**

### 📌 Contoh Penggunaan

Jalankan skrip dan masukkan URL berikut:

```sh
python script.py
```

Saat diminta, masukkan URL:

```
🔗 Masukkan URL YouTube: https://www.youtube.com/watch?v=ktXzFPlHMuk
```

Kemudian, ikuti langkah-langkah berikut:
1. Pilih resolusi video yang diinginkan.
2. Pilih format audio jika ingin mengekstrak atau menggabungkan audio.
3. Tentukan direktori penyimpanan.
4. Video akan diunduh dan diproses secara otomatis.
5. Setelah selesai, file yang telah diproses akan tersedia di direktori yang dipilih.

## ⚠️ Catatan Penting

- Pastikan koneksi internet stabil saat mengunduh video.
- Jika menggunakan **kompresi NVENC**, pastikan driver NVIDIA sudah diperbarui.
- Untuk pengguna macOS/Linux, sesuaikan path FFmpeg dengan lokasi instalasi.
- Jika ada error terkait **yt-dlp**, coba jalankan perintah berikut untuk memperbarui:

```sh
pip install --upgrade yt-dlp
```

## 📞 Dukungan

Jika mengalami kendala, silakan kunjungi [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp) atau [FFmpeg Documentation](https://ffmpeg.org/documentation.html) untuk informasi lebih lanjut.

---

✅ **Skrip ini membantu Anda mengunduh, mengedit, dan mengelola video dengan mudah dan efisien!** 🚀

