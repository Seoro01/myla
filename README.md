# myla

## YouTube audio downloader

Download the audio track of a YouTube video as an MP3.

### Requirements

- Python 3
- ffmpeg (must be on PATH)
- `pip install -r requirements.txt`

### Usage

```
python download_audio.py "https://youtu.be/VIDEO_ID" -o downloads
```

Options:

- `-o, --output-dir`: directory to save the MP3 (default: `downloads`)
- `-q, --quality`: MP3 quality passed to ffmpeg, `0` (best) to `9` (worst); default: `0`

