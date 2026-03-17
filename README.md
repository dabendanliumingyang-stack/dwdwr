# Doraemon Japanese Video Translator

A Doraemon-themed desktop GUI that translates **Japanese videos to English**, generates timed transcripts, and exports a **subtitle-burned output video**.

## Features
- Select a video file (`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`)
- Translate Japanese speech to English with OpenAI Whisper
- Show timestamped transcript in the app
- Export:
  - subtitle-burned output video (`.mp4`)
  - transcript (`.txt`)
  - subtitle file (`.srt`)
- Japanese + Doraemon-inspired visual theme

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Note: You need `ffmpeg` installed and available in PATH for subtitle video export.

## Run
```bash
python translator_gui.py
```

## Usage
1. Click **ファイル選択** and choose a Japanese video.
2. Select model size (`small` default; use `base/tiny` for speed, `medium/large` for quality).
3. Click **翻訳スタート**.
4. Review timestamped English transcript.
5. Click **字幕付き動画を書き出し** to save the final subtitled video plus `.txt` and `.srt`.
