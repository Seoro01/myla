#!/usr/bin/env python3
"""Download the audio track of a YouTube video as an MP3 file.

Usage:
    python download_audio.py <youtube_url> [-o OUTPUT_DIR] [-q QUALITY]

Requires yt-dlp (pip install -r requirements.txt) and ffmpeg on PATH.
"""
import argparse
import sys

from yt_dlp import YoutubeDL


def download_audio(url: str, output_dir: str = "downloads", quality: str = "0") -> str:
    options = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }
        ],
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-o", "--output-dir", default="downloads", help="Directory to save the MP3 (default: downloads)")
    parser.add_argument("-q", "--quality", default="0", help="MP3 quality passed to ffmpeg, 0 (best) to 9 (worst); default: 0")
    args = parser.parse_args()

    path = download_audio(args.url, args.output_dir, args.quality)
    print(f"Saved: {path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
