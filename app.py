import os
import re
import uuid
import subprocess
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__)

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# ─── Helpers ────────────────────────────────────────────────────────────────

def human_size(path: Path) -> str:
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def build_yt_dlp_cmd(url: str, quality: str, output_path: str) -> list[str]:
    """Build the yt-dlp command based on quality choice."""
    base = ["yt-dlp", "--no-playlist", "-o", output_path]

    if quality == "audio":
        return base + [
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            url
        ]

    format_map = {
        "best":  "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "1080":  "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
        "720":   "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
        "480":   "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]",
    }
    fmt = format_map.get(quality, format_map["best"])
    return base + ["-f", fmt, "--merge-output-format", "mp4", url]


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    quality = (data.get("quality") or "best").strip()

    # Basic validation
    if not url:
        return jsonify(error="URL manquante."), 400
    if not re.match(r"https?://t\.me/", url):
        return jsonify(error="Seuls les liens t.me sont acceptés."), 400

    # Unique output filename
    uid = uuid.uuid4().hex[:8]
    ext = "mp3" if quality == "audio" else "mp4"
    filename = f"video_{uid}.{ext}"
    output_path = str(DOWNLOAD_DIR / filename)

    cmd = build_yt_dlp_cmd(url, quality, output_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 min max
        )
    except subprocess.TimeoutExpired:
        return jsonify(error="Délai dépassé (>5 min). La vidéo est peut-être trop longue."), 504
    except FileNotFoundError:
        return jsonify(error="yt-dlp n'est pas installé sur le serveur."), 500

    if result.returncode != 0:
        # yt-dlp error — extract last meaningful line
        err_lines = [l for l in result.stderr.splitlines() if l.strip()]
        err_msg = err_lines[-1] if err_lines else "Erreur inconnue de yt-dlp"
        # Friendly messages
        if "Private" in err_msg or "private" in err_msg:
            err_msg = "Cette vidéo est privée ou nécessite une connexion."
        elif "Unable to extract" in err_msg:
            err_msg = "Impossible d'extraire la vidéo. Vérifiez que le lien est public."
        return jsonify(error=err_msg), 422

    file_path = Path(output_path)
    if not file_path.exists():
        return jsonify(error="Le fichier n'a pas été créé. Vérifiez le lien."), 500

    return jsonify(
        filename=filename,
        size=human_size(file_path)
    )


@app.route("/file/<filename>")
def serve_file(filename):
    """Serve the downloaded file."""
    # Security: only alphanumeric + underscore + dot
    if not re.match(r'^[\w\-.]+$', filename):
        return "Fichier invalide", 400
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


# ─── Cleanup (optional cron) ─────────────────────────────────────────────────

def cleanup_old_files(max_age_minutes=60):
    """Delete files older than max_age_minutes."""
    import time
    now = time.time()
    for f in DOWNLOAD_DIR.iterdir():
        if f.is_file() and (now - f.stat().st_mtime) > max_age_minutes * 60:
            f.unlink(missing_ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
