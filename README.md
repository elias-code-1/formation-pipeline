# Formation – Pipeline Montage Vidéo 🎬

Pipeline automatisé de montage vidéo pour 6 modules de formation.

## 📁 Structure

```
.
├── _work/
│   ├── scripts/
│   │   ├── full_pipeline.py    # Pipeline principal
│   │   └── convert_fps.py      # Conversion FPS
│   └── module-N/               # Fichiers intermédiaires (non versionnés)
├── module-N/                   # Vidéos finales par module
├── .github/
│   └── workflows/
│       └── pipeline.yml        # GitHub Actions CI
└── requirements.txt
```

## 🚀 Lancer le pipeline

### Localement

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python _work/scripts/full_pipeline.py
```

### Via GitHub Actions

Aller dans l'onglet **Actions** du dépôt → **Pipeline Montage Formation** → **Run workflow**.

> ⚠️ Les vidéos brutes (*.mp4, *.m4a) ne sont pas versionnées. Elles doivent être présentes localement ou uploadées dans les **GitHub Actions secrets / artifacts** avant le run.

## 🧩 Modules

| Module | Vidéo source | Audio |
|--------|-------------|-------|
| 1 | `2026-11-07 22-31-30.mp4` | `Formation module 1.m4a` |
| 2 | `2026-11-08 03-51-29.mp4` | `Module 2_6.m4a` |
| 3 | `2026-11-08 09-30-52.mp4` | `Module 3_6.m4a` |
| 4 | `2026-11-08 10-05-19.mp4` | `Module 4_6.m4a` |
| 5 | `edit capcut demo.mp4` | `Module 5_6 voix off.m4a` |
| 6 | `video-final.mov` | `Module 6 recap.m4a` |

## 🛠️ Dépendances

- Python 3.12+
- ffmpeg (installé sur le système)
- faster-whisper
- Voir `requirements.txt`
