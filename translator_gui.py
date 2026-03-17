#!/usr/bin/env python3
"""Doraemon-inspired Japanese themed GUI for translating Japanese video to English with timestamps."""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import whisper
except ImportError:  # pragma: no cover - handled at runtime
    whisper = None


class DoraemonTranslatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("どらえもん翻訳スタジオ | Doraemon Translation Studio")
        self.root.geometry("980x700")
        self.root.configure(bg="#8ED6FF")

        self.video_path = tk.StringVar()
        self.model_size = tk.StringVar(value="small")

        self._build_style()
        self._build_ui()

    def _build_style(self) -> None:
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("Primary.TFrame", background="#8ED6FF")
        self.style.configure(
            "Card.TFrame",
            background="#FFFFFF",
            relief="flat",
        )
        self.style.configure(
            "Title.TLabel",
            background="#8ED6FF",
            foreground="#003B73",
            font=("Yu Gothic UI", 20, "bold"),
        )
        self.style.configure(
            "Sub.TLabel",
            background="#8ED6FF",
            foreground="#003B73",
            font=("Yu Gothic UI", 11),
        )
        self.style.configure(
            "CardTitle.TLabel",
            background="#FFFFFF",
            foreground="#0A4D8C",
            font=("Yu Gothic UI", 13, "bold"),
        )
        self.style.configure(
            "Action.TButton",
            font=("Yu Gothic UI", 11, "bold"),
            background="#0078D7",
            foreground="#FFFFFF",
            borderwidth=0,
            focusthickness=3,
            focuscolor="none",
            padding=(10, 8),
        )
        self.style.map(
            "Action.TButton",
            background=[("active", "#005AA6"), ("disabled", "#A6A6A6")],
        )

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, style="Primary.TFrame", padding=18)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            style="Title.TLabel",
            text="🐾 どらえもん翻訳スタジオ",
        ).pack(anchor="center", pady=(0, 4))

        ttk.Label(
            container,
            style="Sub.TLabel",
            text="日本語の動画を英語へ翻訳し、タイムスタンプ付きの字幕を作成します",
        ).pack(anchor="center", pady=(0, 16))

        config_card = ttk.Frame(container, style="Card.TFrame", padding=14)
        config_card.pack(fill="x")

        ttk.Label(config_card, style="CardTitle.TLabel", text="📼 動画入力").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        path_frame = ttk.Frame(config_card, style="Card.TFrame")
        path_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        config_card.columnconfigure(0, weight=1)
        path_frame.columnconfigure(0, weight=1)

        self.path_entry = tk.Entry(
            path_frame,
            textvariable=self.video_path,
            font=("Yu Gothic UI", 11),
            relief="solid",
            bd=1,
        )
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ttk.Button(
            path_frame,
            text="ファイル選択",
            style="Action.TButton",
            command=self._pick_file,
        ).grid(row=0, column=1)

        model_frame = ttk.Frame(config_card, style="Card.TFrame")
        model_frame.grid(row=2, column=0, sticky="w", pady=(4, 0))

        ttk.Label(
            model_frame,
            style="CardTitle.TLabel",
            text="モデルサイズ:",
        ).grid(row=0, column=0, padx=(0, 8))

        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_size,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=12,
            font=("Yu Gothic UI", 10),
        )
        model_combo.grid(row=0, column=1)

        action_frame = ttk.Frame(container, style="Primary.TFrame")
        action_frame.pack(fill="x", pady=12)

        self.translate_btn = ttk.Button(
            action_frame,
            text="🚀 翻訳スタート",
            style="Action.TButton",
            command=self._start_translation,
        )
        self.translate_btn.pack(side="left")

        self.save_btn = ttk.Button(
            action_frame,
            text="💾 結果を保存",
            style="Action.TButton",
            command=self._save_results,
            state="disabled",
        )
        self.save_btn.pack(side="left", padx=10)

        self.status_var = tk.StringVar(value="準備完了: 動画ファイルを選択してください。")
        ttk.Label(
            container,
            style="Sub.TLabel",
            textvariable=self.status_var,
        ).pack(anchor="w", pady=(0, 6))

        self.progress = ttk.Progressbar(container, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 10))

        output_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        output_card.pack(fill="both", expand=True)

        ttk.Label(
            output_card,
            style="CardTitle.TLabel",
            text="📝 英語字幕（タイムスタンプ付き）",
        ).pack(anchor="w")

        self.output_text = tk.Text(
            output_card,
            wrap="word",
            font=("Consolas", 10),
            bg="#F8FCFF",
            fg="#1A1A1A",
            relief="solid",
            bd=1,
        )
        self.output_text.pack(fill="both", expand=True, pady=(8, 0))

        self.segments = []

    def _pick_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="日本語動画を選択",
            filetypes=[
                ("Video Files", "*.mp4 *.mkv *.avi *.mov *.webm"),
                ("All Files", "*.*"),
            ],
        )
        if selected:
            self.video_path.set(selected)

    def _start_translation(self) -> None:
        if whisper is None:
            messagebox.showerror(
                "Missing Dependency",
                "Package 'whisper' is not installed.\nRun: pip install openai-whisper",
            )
            return

        video_file = self.video_path.get().strip()
        if not video_file:
            messagebox.showwarning("入力エラー", "動画ファイルを選択してください。")
            return

        if not os.path.exists(video_file):
            messagebox.showerror("ファイルエラー", "指定した動画ファイルが見つかりません。")
            return

        self.translate_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.progress.start(8)
        self.status_var.set("翻訳中... 少し待ってください（Doraemon power!）")
        self.output_text.delete("1.0", tk.END)

        worker = threading.Thread(target=self._translate_worker, daemon=True)
        worker.start()

    def _translate_worker(self) -> None:
        try:
            model = whisper.load_model(self.model_size.get())
            result = model.transcribe(
                self.video_path.get(),
                language="ja",
                task="translate",
                verbose=False,
            )
            self.segments = result.get("segments", [])
            formatted = self._format_segments(self.segments)
            self.root.after(0, self._on_translation_success, formatted)
        except Exception as exc:  # pragma: no cover - runtime path
            self.root.after(0, self._on_translation_error, str(exc))

    def _on_translation_success(self, formatted_text: str) -> None:
        self.progress.stop()
        self.translate_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.status_var.set("翻訳完了！結果を確認して保存できます。")
        self.output_text.insert(tk.END, formatted_text)

    def _on_translation_error(self, err: str) -> None:
        self.progress.stop()
        self.translate_btn.configure(state="normal")
        self.status_var.set(f"エラー: {err}")
        messagebox.showerror("Translation Error", err)

    def _save_results(self) -> None:
        if not self.segments:
            messagebox.showwarning("保存エラー", "保存できる結果がありません。")
            return

        base_path = filedialog.asksaveasfilename(
            title="結果保存",
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
            initialfile="translated_transcript.txt",
        )

        if not base_path:
            return

        txt_content = self._format_segments(self.segments)
        srt_content = self._to_srt(self.segments)
        srt_path = os.path.splitext(base_path)[0] + ".srt"

        with open(base_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(txt_content)

        with open(srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(srt_content)

        messagebox.showinfo("保存完了", f"保存しました:\n{base_path}\n{srt_path}")

    @staticmethod
    def _format_ts(seconds: float) -> str:
        total_ms = int(seconds * 1000)
        ms = total_ms % 1000
        total_seconds = total_ms // 1000
        sec = total_seconds % 60
        mins = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        return f"{hours:02}:{mins:02}:{sec:02}.{ms:03}"

    def _format_segments(self, segments: list[dict]) -> str:
        lines = []
        for seg in segments:
            start = self._format_ts(seg.get("start", 0.0))
            end = self._format_ts(seg.get("end", 0.0))
            text = seg.get("text", "").strip()
            lines.append(f"[{start} --> {end}] {text}")
        return "\n".join(lines)

    @staticmethod
    def _to_srt(segments: list[dict]) -> str:
        def fmt_srt(seconds: float) -> str:
            total_ms = int(seconds * 1000)
            ms = total_ms % 1000
            total_seconds = total_ms // 1000
            sec = total_seconds % 60
            mins = (total_seconds // 60) % 60
            hours = total_seconds // 3600
            return f"{hours:02}:{mins:02}:{sec:02},{ms:03}"

        blocks = []
        for i, seg in enumerate(segments, start=1):
            start = fmt_srt(seg.get("start", 0.0))
            end = fmt_srt(seg.get("end", 0.0))
            text = seg.get("text", "").strip()
            blocks.append(f"{i}\n{start} --> {end}\n{text}\n")
        return "\n".join(blocks)


def main() -> None:
    root = tk.Tk()
    app = DoraemonTranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
