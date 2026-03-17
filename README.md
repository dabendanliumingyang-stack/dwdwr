# Doraemon Japanese Video Translator

A Doraemon-themed desktop GUI that translates **Japanese videos to English** and outputs transcript text with timing.

## Features
- Select a video file (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`)
- Translate Japanese speech to English with OpenAI Whisper
- Show timestamped transcript in the app
- Save output as both `.txt` and `.srt`
- Japanese + Doraemon-inspired visual theme

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Note: Whisper uses FFmpeg under the hood. Install `ffmpeg` if not already available.

## Run
```bash
python translator_gui.py
```

## Usage
1. Click **ファイル選択** and choose a Japanese video.
2. Select model size (`small` default; use `base/tiny` for speed, `medium/large` for quality).
3. Click **翻訳スタート**.
4. Review timestamped English transcript.
5. Click **結果を保存** to save `.txt` + `.srt`.
