#!/usr/bin/env python3
"""Download a YouTube video's audio track as an MP3 file.

Usage:
    python3 scripts/download_youtube_audio.py <youtube-url> [output-dir]

Requires yt-dlp (`pip install yt-dlp`) and ffmpeg on PATH.
"""
import shutil
import sys


def ensure_dependencies() -> None:
    missing = []
    if shutil.which("ffmpeg") is None:
        missing.append("ffmpeg (install via your OS package manager)")
    try:
        import yt_dlp  # noqa: F401
    except ImportError:
        missing.append("yt-dlp (pip install yt-dlp)")
    if missing:
        print("Missing dependencies:", file=sys.stderr)
        for item in missing:
            print(f"  - {item}", file=sys.stderr)
        sys.exit(1)


def download(url: str, output_dir: str) -> None:
    import yt_dlp

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <youtube-url> [output-dir]", file=sys.stderr)
        sys.exit(1)

    ensure_dependencies()
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    download(url, output_dir)


if __name__ == "__main__":
    main()
