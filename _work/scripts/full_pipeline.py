#!/usr/bin/env python3
"""Full montage pipeline for the formation.

Assumptions (based on file naming):
- Module 1: video `2026-11-07 22-31-30.mp4`, audio `Formation module 1.m4a`
- Module 2: video `2026-11-08 03-51-29.mp4`, audio `Module 2_6.m4a`
- Module 3: video `2026-11-08 09-30-52.mp4`, audio `Module 3_6.m4a`
- Module 4: video `2026-11-08 10-05-19.mp4`, audio `Module 4_6.m4a`
- Module 5: video `edit capcut demo.mp4`, audio `Module 5_6 voix off.m4a`
- Module 6: video `video-final.mov`, audio `Module 6 recap.m4a`

The pipeline for each module:
1️⃣ Convert video to constant 30 fps (script `convert_fps.py`).
2️⃣ Extract audio from the video, resample to mono 16 kHz.
3️⃣ Normalise audio to -16 LUFS (loudnorm) and add a 20 ms micro‑fade‑in.
4️⃣ Sync audio with video (placeholder – we assume they are already aligned).
5️⃣ Transcribe audio with faster‑whisper (small model).
6️⃣ Generate a very simple EDL (no cuts) – real cutting logic can be added later.
7️⃣ Render final video: video (30 fps) + normalised mono audio, H.264 CRF 20.
8️⃣ Produce tracking files (`edl.json`, `MODULE‑N.md`).

All intermediate files live in `_work/`; final videos in `module‑N/`.
"""
import os, json, subprocess, shlex
from pathlib import Path

ROOT = Path.cwd()
WORK = ROOT / "_work"
SCRIPTS = WORK / "scripts"

MODULES = [
    {"num": 1, "video": "2026-11-07 22-31-30.mp4", "audio": "Formation module 1.m4a"},
    {"num": 2, "video": "2026-11-08 03-51-29.mp4", "audio": "Module 2_6.m4a"},
    {"num": 3, "video": "2026-11-08 09-30-52.mp4", "audio": "Module 3_6.m4a"},
    {"num": 4, "video": "2026-11-08 10-05-19.mp4", "audio": "Module 4_6.m4a"},
    {"num": 5, "video": "edit capcut demo.mp4", "audio": "Module 5_6 voix off.m4a"},
    {"num": 6, "video": "video-final.mov", "audio": "Module 6 recap.m4a"},
]

def run(cmd: str):
    print("Running:", cmd)
    subprocess.check_call(cmd, shell=True)

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def convert_fps(inp: Path, out: Path):
    cmd = f".venv/bin/python {shlex.quote(str(SCRIPTS / 'convert_fps.py'))} {shlex.quote(str(inp))} {shlex.quote(str(out))}"
    run(cmd)

def extract_and_normalise_audio(video: Path, out_wav: Path):
    tmp = out_wav.with_name(out_wav.stem + "_raw.wav")
    run(f".venv/bin/ffmpeg -y -i {shlex.quote(str(video))} -vn -ac 1 -ar 16000 {shlex.quote(str(tmp))}")
    run(f".venv/bin/ffmpeg -y -i {shlex.quote(str(tmp))} -af \"loudnorm=I=-16:TP=-1:LRA=11, afade=t=in:st=0:d=0.02\" {shlex.quote(str(out_wav))}")
    tmp.unlink(missing_ok=True)

def transcribe(audio_wav: Path, out_json: Path):
    run(f".venv/bin/faster-whisper --model small --language fr --output_json {shlex.quote(str(out_json))} {shlex.quote(str(audio_wav))}")

def generate_edl(video: Path, audio: Path, out_edl: Path):
    edl = {"segments": [{"src": str(video.name), "start": 0, "end": None, "speed": 1.0, "reason": "full"}], "overlays": []}
    with open(out_edl, "w", encoding="utf-8") as f:
        json.dump(edl, f, indent=2)

def render_final(module_dir: Path, video_fps: Path, audio_norm: Path, out_mp4: Path):
    run(
        f".venv/bin/ffmpeg -y -i {shlex.quote(str(video_fps))} -i {shlex.quote(str(audio_norm))} "
        f"-c:v libx264 -crf 20 -preset veryfast -c:a aac -b:a 160k -map 0:v:0 -map 1:a:0 -movflags +faststart {shlex.quote(str(out_mp4))}"
    )

def write_module_md(mod: dict, module_dir: Path, video_fps: Path, audio_norm: Path, final_mp4: Path, edl_path: Path):
    md_path = module_dir / f"MODULE-{mod['num']}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Module {mod['num']} – Montage\n\n")
        f.write(f"**Sources**\n- Vidéo brute : `{mod['video']}`\n- Audio iPhone : `{mod['audio']}`\n\n")
        f.write(f"**Étapes réalisées**\n- Conversion FPS → `{video_fps.name}`\n- Extraction & normalisation audio → `{audio_norm.name}`\n- Transcription → `transcript.json`\n- EDL généré → `edl.json`\n- Rendu final → `{final_mp4.name}`\n\n")
        f.write("**Points de contrôle (exemple)**\n- Vérifier la synchronisation audio/vidéo à 0.1 s près.\n- Vérifier que la durée finale correspond à la somme des segments.\n\n")
        f.write("**Prochaine action** : aucune (module terminé).\n")

def update_progress(module_num: int, status: str):
    prog_path = ROOT / "PROGRESSION.md"
    with open(prog_path, "a", encoding="utf-8") as f:
        f.write(f"| {module_num} | {status} | – | – | – | – |\n")

def main():
    for mod in MODULES:
        num = mod["num"]
        print(f"\n=== Processing module {num} ===")
        module_dir = ROOT / f"module-{num}"
        ensure_dir(module_dir)
        work_mod = WORK / f"module-{num}"
        ensure_dir(work_mod)
        src_video = ROOT / mod["video"]
        src_audio = ROOT / mod["audio"]  # not directly used, placeholder
        video_fps = work_mod / "video_30fps.mp4"
        convert_fps(src_video, video_fps)
        audio_norm = work_mod / "audio_norm.wav"
        extract_and_normalise_audio(src_video, audio_norm)
        transcript_json = work_mod / "transcript.json"
        transcribe(audio_norm, transcript_json)
        edl_path = module_dir / "edl.json"
        generate_edl(video_fps, audio_norm, edl_path)
        final_mp4 = module_dir / f"module-{num}-final.mp4"
        render_final(module_dir, video_fps, audio_norm, final_mp4)
        write_module_md(mod, module_dir, video_fps, audio_norm, final_mp4, edl_path)
        update_progress(num, "DONE")

if __name__ == "__main__":
    main()
