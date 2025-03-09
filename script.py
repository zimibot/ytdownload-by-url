import yt_dlp
import os
import sys
import subprocess
import time
import re


def ensure_directory(path):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def get_video_id(url):
    """Extract video ID from the YouTube URL."""
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict.get('id', 'unknown_id')

def progress_hook(d):
    """Menampilkan progress download secara real-time"""
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        eta = d['_eta_str']
        sys.stdout.write(f"\r⏳ Mengunduh... {percent} (Sisa waktu: {eta})")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\n✅ Download selesai!")

def list_avc1_formats(url):
    """Menampilkan daftar resolusi MP4 yang mendukung codec AVC1 dan sejenisnya"""
    print("\n🔄 Mengambil daftar resolusi (hanya AVC1, VP9, AV1)...")
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

    formats = info_dict.get('formats', [])
    available_formats = {}

    print("\n=== Pilihan Resolusi Video (AVC1, VP9, AV1) ===")
    for fmt in formats:
        if 'mp4' in fmt.get('ext', '') and ('avc1' in fmt.get('vcodec', '') or 'vp9' in fmt.get('vcodec', '') or 'av01' in fmt.get('vcodec', '')):
            format_id = fmt.get('format_id')
            res = fmt.get('format_note', 'Unknown')
            fps = fmt.get('fps', 'N/A')
            filesize = fmt.get('filesize', 'Tidak diketahui') if fmt.get('filesize') is None else f"{fmt.get('filesize') / 1024 / 1024:.2f} MB"
            acodec = fmt.get('acodec', 'unknown')

            # Tandai jika hanya video tanpa audio
            audio_status = "✅ Audio" if acodec != "none" else "❌ No Audio"

            available_formats[format_id] = {"res": res, "audio": acodec != "none"}
            print(f"ID: {format_id} | Resolusi: {res} | FPS: {fps} | Ukuran: {filesize} | {audio_status}")

    return available_formats, info_dict
def list_video_formats_with_audio(info_dict):
    """Menampilkan semua format video yang memiliki audio"""
    print("\n🔄 Mengambil daftar format video dengan audio...")
    formats = info_dict.get('formats', [])
    available_formats = {}

    print("\n=== Daftar Format Video dengan Audio ===")
    for fmt in formats:
        acodec = fmt.get('acodec', 'unknown')
        if acodec == "none":
            continue  # Lewati format tanpa audio

        format_id = fmt.get('format_id')
        res = fmt.get('format_note', 'Unknown')
        fps = fmt.get('fps', 'N/A')
        ext = fmt.get('ext', 'Unknown')
        filesize = fmt.get('filesize', 'Tidak diketahui') if fmt.get('filesize') is None else f"{fmt.get('filesize') / 1024 / 1024:.2f} MB"
        vcodec = fmt.get('vcodec', 'unknown')

        available_formats[format_id] = {"res": res, "fps": fps, "ext": ext, "vcodec": vcodec}
        print(f"ID: {format_id} | Resolusi: {res} | FPS: {fps} | Format: {ext} | Ukuran: {filesize} | Codec: {vcodec} | ✅ Audio")

    return available_formats


def download_file(url, format_id, output_path):
    """Mengunduh file video/audio berdasarkan format_id"""
    output_file = os.path.join(output_path, f"temp_{format_id}.mp4")
    print(f"\n🔽 Mengunduh: {output_file}...")
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_file,
        'progress_hooks': [progress_hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_file

def extract_audio(input_file, output_audio_file):
    """Ekstrak audio dari file video"""
    print("\n🎵 Mengekstrak audio dari video...")
    command = f"ffmpeg -i \"{input_file}\" -q:a 0 -map a \"{output_audio_file}\" -y"
    subprocess.run(command, shell=True, check=True)
    print(f"✅ Audio diekstrak: {output_audio_file}")

def merge_video_audio(video_file, audio_file, output_file):
    """Gabungkan video dan audio menggunakan FFmpeg"""
    print("\n🛠️ Menggabungkan video dan audio...")
    command = f"ffmpeg -i \"{video_file}\" -i \"{audio_file}\" -c:v copy -c:a aac \"{output_file}\" -y"
    subprocess.run(command, shell=True, check=True)
    print(f"✅ Video final telah dibuat: {output_file}")



def get_file_size(file_path):
    """Mengembalikan ukuran file dalam MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def compress_video(input_file, output_file, target_ratio=0.40, max_attempts=5):
    """
    Mengompresi video hingga ukurannya mencapai target_ratio dari ukuran asli.
    target_ratio = 0.40 berarti video dikurangi 60% dari ukuran awal.
    """
    print("\n📉 Mengompresi video dengan GPU NVIDIA (NVENC) dengan target 60% lebih kecil...")

    # Pastikan file input ada
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' tidak ditemukan.")
        sys.exit(1)

    # Pastikan folder output tersedia
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Ambil ukuran file asli
    original_size = get_file_size(input_file)
    target_size = original_size * target_ratio
    print(f"📏 Ukuran asli: {original_size:.2f} MB | Target ukuran: {target_size:.2f} MB")

    # Pilih encoder GPU yang tersedia
    try:
        result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True)
        encoder = "hevc_nvenc" if "nvenc" in result.stdout else "libx265"
    except Exception as e:
        print(f"⚠️ Gagal mengecek encoder: {e}")
        encoder = "libx265"

    # **Iterasi untuk menemukan pengaturan terbaik yang mencapai target ukuran**
    crf = 28  # Mulai dengan kualitas standar
    bitrate = 2  # Awal bitrate 2 Mbps
    attempt = 0

    while attempt < max_attempts:
        print(f"\n🛠️ Percobaan {attempt + 1}: CRF={crf}, Bitrate={bitrate}M")

        # Format perintah FFmpeg
        command = [
            "ffmpeg", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
            "-i", input_file,
            "-c:v", encoder, "-preset", "slow", "-cq", str(crf),
            "-b:v", f"{bitrate}M", "-maxrate", f"{bitrate * 2}M", "-bufsize", f"{bitrate * 4}M",
            "-c:a", "aac", "-b:a", "128k",
            "-threads", "8",
            output_file, "-y"
        ]

        # Jalankan proses kompresi dengan progress
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # **Progress Monitoring**
        duration_total = None
        for line in process.stderr:
            sys.stdout.write(line)
            sys.stdout.flush()

            # Ambil total durasi video
            match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                duration_total = hours * 3600 + minutes * 60 + seconds

            # Ambil progress encoding
            match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
            if match and duration_total:
                hours, minutes, seconds = map(float, match.groups())
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = (current_time / duration_total) * 100
                sys.stdout.write(f"\r⏳ Progress: {progress:.2f}%")
                sys.stdout.flush()

        process.wait()

        # Cek ukuran file hasil
        time.sleep(2)  # Tunggu sebentar agar sistem menulis file
        if not os.path.exists(output_file):
            print("\n❌ Error: File hasil kompresi tidak ditemukan!")
            sys.exit(1)

        compressed_size = get_file_size(output_file)
        print(f"\n📏 Ukuran setelah kompresi: {compressed_size:.2f} MB")

        # **Cek apakah ukuran sudah sesuai target**
        if compressed_size <= target_size:
            print(f"\n✅ Berhasil! Ukuran video dikurangi hingga {100 - (compressed_size/original_size)*100:.2f}%")
            break
        else:
            print(f"⚠️ Ukuran masih terlalu besar, menyesuaikan parameter...")
            crf += 2  # Naikkan CRF (lebih tinggi = lebih kecil)
            bitrate -= 0.5  # Kurangi bitrate sedikit
            attempt += 1
            os.remove(output_file)  # Hapus file lama untuk mencoba lagi

    if attempt == max_attempts:
        print("\n⚠️ Gagal mencapai ukuran target setelah beberapa percobaan.")
        print(f"📏 Ukuran akhir: {compressed_size:.2f} MB dari target {target_size:.2f} MB")

    print(f"\n✅ Video final: {output_file} ({compressed_size:.2f} MB)")


def split_video(input_file, output_folder, duration_per_part=300, resolution="1280:720"):
    print("\n✂️ Membagi video menjadi beberapa bagian dengan GPU NVIDIA (Encoding NVENC)...")

    font_path = "C\\:/Users/Harris/Downloads/Downloadyt/font/roboto.ttf"

    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' tidak ditemukan.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    total_parts = get_file_duration(input_file) // duration_per_part + 1

    for part in range(total_parts):
        part_number = part + 1
        output_file = os.path.join(output_folder, f"part_{part_number:02d}.mp4")

        drawtext_filter = (
            f"drawtext=text='Part {part_number}/{total_parts}':"
            f"fontfile='{font_path}':"
            "fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h-text_h-20"
        )

        pad_filter = "pad=w=iw+100:h=ih+100:x=50:y=50:color=green"
        filters = f"{pad_filter},{drawtext_filter}"

        command = [
            "ffmpeg",
            "-i", input_file,
            "-ss", str(part * duration_per_part),
            "-t", str(duration_per_part),
            "-vf", filters,
            "-vf", f"scale={resolution}",
            "-c:v", "h264_nvenc",
            "-b:v", "1M", 
            "-preset", "slow",  
            "-maxrate:v", "1.5M",
            "-bufsize:v", "2M",
            "-c:a", "aac",
            "-b:a", "96k", 
            output_file,
            "-y"
        ]

        process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)

        for line in process.stderr:
            match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = (current_time / duration_per_part) * 100
                sys.stdout.write(f"\r⏳ Part {part_number}/{total_parts} - Progress: {progress:.2f}%")
                sys.stdout.flush()

        process.wait()

        if process.returncode != 0:
            print(f"\n❌ Error saat membagi video Part {part_number}!")
            sys.exit(1)

        print(f"\n✅ Part {part_number}/{total_parts} selesai: {output_file}")

    print(f"\n✅ Semua video berhasil diproses dan disimpan di: {output_folder}")

def get_file_duration(input_file):
    result = subprocess.run(
        ["ffprobe", "-i", input_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    return int(float(result.stdout.strip()))

            
def get_file_duration(input_file):
    result = subprocess.run(
        ["ffprobe", "-i", input_file, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    return int(float(result.stdout.strip()))

if __name__ == "__main__":
    url = input("🔗 Masukkan URL YouTube: ")
    video_id = get_video_id(url)
    
    output_path = input("\n📁 Masukkan path untuk menyimpan video (kosongkan untuk direktori saat ini): ").strip() or os.getcwd()
    output_base = os.path.join(output_path, "output", video_id, "files")
    
    ensure_directory(output_base)

    available_formats, info_dict = list_avc1_formats(url)
    selected_video_format = input("\n🎥 Masukkan ID resolusi video yang diinginkan: ").strip()

    video_formats = list_video_formats_with_audio(info_dict)
    selected_audio_format = input("\n🎵 Masukkan ID format yang akan dikonversi ke audio: ").strip()

    video_file = download_file(url, selected_video_format, output_base)
    audio_file = download_file(url, selected_audio_format, output_base)

    extracted_audio = os.path.join(output_base, "selected_audio.mp3")
    extract_audio(audio_file, extracted_audio)

    final_output = os.path.join(output_base, "final_video.mp4")
    merge_video_audio(video_file, extracted_audio, final_output)
    
    output_folder = os.path.join(output_base, "split_videos")

    duration = int(input("\n⏳ Masukkan durasi per bagian (detik): ").strip())
    resolution = input("\n📏 Masukkan resolusi video (misal: 1280:720, 1920:1080, default: 1280:720): ").strip()
    
    split_video(final_output, output_folder, duration, resolution)
    

    print("\n✅ Semua proses selesai! Video terbagi di folder:", output_folder)
