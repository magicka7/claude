#!/usr/bin/env python3
"""
Transcribe videos/audio to .txt using faster-whisper.

Usage:
  .venv-whisper/bin/python scripts/transcribe.py "carpeta/clase 1.mp4" ["carpeta/clase 2.mp4" ...]
  .venv-whisper/bin/python scripts/transcribe.py --folder "Salud infantil"
  .venv-whisper/bin/python scripts/transcribe.py --folder "Salud Humana"   # recorre subcarpetas (Modulo 1, etc.)

Output: for each input "algo.mp4" writes "algo.txt" next to it (strips a
trailing space in the stem, e.g. "Clase 2 .mp4" -> "Clase 2.txt"), in the
same [HH:MM:SS --> HH:MM:SS] texto format used across this project. Skips
files whose .txt already exists.
"""
import argparse
import os
import subprocess
import sys
import time

VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm", ".m4a", ".mp3", ".wav")


def fmt(t):
    h = int(t) // 3600
    m = (int(t) % 3600) // 60
    s = int(t) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def out_path_for(video_path):
    folder, name = os.path.split(video_path)
    stem, _ = os.path.splitext(name)
    return os.path.join(folder, stem.strip() + ".txt")


def transcribe_one(model, video_path, tmp_dir):
    out_path = out_path_for(video_path)
    if os.path.exists(out_path):
        print(f"SKIP (exists): {out_path}", flush=True)
        return

    print(f"START: {video_path}", flush=True)
    t0 = time.time()

    wav_path = os.path.join(tmp_dir, "audio_tmp.wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
         "-ar", "16000", "-ac", "1", wav_path, "-loglevel", "error"],
        check=True,
    )

    segments, info = model.transcribe(wav_path, language="es", beam_size=1)
    lines = [f"[{fmt(s.start)} --> {fmt(s.end)}] {s.text.strip()}" for s in segments]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    os.remove(wav_path)
    print(f"DONE: {out_path} ({time.time()-t0:.0f}s, {len(lines)} segments)", flush=True)


def collect_files(args):
    files = list(args.files)
    if args.folder:
        for root, dirs, names in os.walk(args.folder):
            dirs.sort()
            for name in sorted(names):
                if name.lower().endswith(VIDEO_EXTS):
                    files.append(os.path.join(root, name))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="video/audio files to transcribe")
    parser.add_argument("--folder", help="transcribe every video/audio file in this folder, recursively")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large-v3"],
                         help="faster-whisper model size (default: small, fast on CPU)")
    parser.add_argument("--lang", default="es", help="language code (default: es)")
    args = parser.parse_args()

    files = collect_files(args)
    if not files:
        print("No files given. Use positional args or --folder.", file=sys.stderr)
        sys.exit(1)

    from faster_whisper import WhisperModel
    print(f"Loading model {args.model}...", flush=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print("Model loaded.", flush=True)

    tmp_dir = os.path.dirname(os.path.abspath(__file__))
    for f in files:
        transcribe_one(model, f, tmp_dir)

    print("ALL_DONE", flush=True)


if __name__ == "__main__":
    main()
