This repository contains `ocr_transcribe.py`, a small Python script that uses
pytesseract to OCR images and create a markdown file (e.g. `chapter_1.md`).

Prerequisites

- Tesseract OCR must be installed on your machine and the `tesseract` binary must be on PATH.

Install Tesseract (platform-specific)

- macOS:

  ```bash
  brew install tesseract
  ```

- Linux (Debian/Ubuntu) or Windows (WSL):

  ```bash
  sudo apt update
  sudo apt install -y tesseract-ocr libtesseract-dev
  ```

Install Python dependencies in your venv (on Windows or inside WSL). We pin a
small set of packages here; adjust versions if needed.

Using pip:

```bash
python -m pip install numpy pillow pytesseract
```

Using uv (if you prefer to manage packages with uv):

```bash
uv add numpy pillow pytesseract
```

Run the script on your chapter folder:

```bash
python ocr_transcribe.py --input-dir static/chapter_1 --output-file chapter_1.md
```

Or run the script using `uv run` (uses the active uv environment):

```bash
uv run python ocr_transcribe.py --input-dir static/chapter_1 --output-file chapter_1.md
```

Options:

- `--resize`: max width in pixels to resize images before OCR (default 2000).
- `--lang`: tesseract language codes (default `eng`).

Notes on privacy and cost:

- Script runs locally with `pytesseract` so your images are not uploaded.

If you want, I can add a small helper to compress/resize images prior to uploading to an API, but given your preference for local processing this README guides running under WSL for Windows users.
