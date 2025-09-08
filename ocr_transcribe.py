#!/usr/bin/env python3
"""ocr_transcribe.py

Simple OCR transcription tool using pytesseract (default).

Writes a markdown file with pages in order. Attempts to detect page numbers from
the OCR text and sort by them; falls back to filename order.

Usage:
  python ocr_transcribe.py --input-dir static/chapter_1 --output-file chapter_1.md

Optional args: --resize (max width in px), --engine (pytesseract|easyocr), --lang
"""
import argparse
from pathlib import Path
from typing import Optional
from PIL import Image, ImageOps
import pytesseract
import sys


def preprocess_image_pil(img: Image.Image, max_width: Optional[int] = None):
    # convert to grayscale and optionally resize to max_width while keeping aspect
    img = img.convert("L")
    if max_width and img.width > max_width:
        wpercent = max_width / float(img.width)
        hsize = int((float(img.height) * float(wpercent)))
        # use Resampling enum when available (Pillow 9+), fall back otherwise
        try:
            resample = Image.Resampling.LANCZOS
        except Exception:
            resample = Image.LANCZOS # type: ignore
        img = img.resize((max_width, hsize), resample)
    # increase contrast a bit
    img = ImageOps.autocontrast(img)
    return img


def extract_page_number_from_text(text: str):
    """Try a simple, regex-free extraction of a page number.

    Strategy:
    - Look at the last few non-empty lines (tail) and search for the word "page"
      (case-insensitive). If found, parse digits that follow that word.
    - Fallbacks: an isolated numeric line or a "X/Y" fraction where X is the page.
    """
    if not text:
        return None

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    tail = lines[-8:] if len(lines) >= 8 else lines

    # Primary: look for the word 'page' in the tail, parse digits after it.
    for line in reversed(tail):
        low = line.lower()
        if 'page' in low:
            # take the substring after the last occurrence of 'page'
            idx = low.rfind('page')
            after = low[idx + len('page'):].lstrip(' .:-')
            # collect consecutive digits at the start of the substring
            num = ''
            for ch in after:
                if ch.isdigit():
                    num += ch
                elif num:
                    break
            if num:
                try:
                    return int(num)
                except Exception:
                    pass
            # if nothing found after 'page', check any token in the line
            tokens = low.replace('/', ' ').split()
            for t in tokens:
                if t.isdigit():
                    return int(t)

    # Fallback 1: isolated numeric line in tail
    for line in reversed(tail):
        if line.isdigit():
            return int(line)

    # Fallback 2: try 'X/Y' formats where X is the page
    for line in reversed(tail):
        if '/' in line:
            parts = [p.strip() for p in line.split('/') if p.strip()]
            if parts and parts[0].isdigit():
                return int(parts[0])

    return None


def ocr_image_file(path: Path, resize: Optional[int] = None, lang: str = 'eng') -> str:
    try:
        img = Image.open(path)
    except Exception as e:
        print(f"[ERROR] Opening image {path}: {e}")
        return ""
    img = preprocess_image_pil(img, max_width=resize)
    try:
        text = pytesseract.image_to_string(img, lang=lang)
    except Exception:
        print(f"[ERROR] tesseract failed on {path}: tesseract is not installed or it's not in your PATH. See \nREADME file for more information.")
        return ""
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', required=True, help='Directory with images')
    p.add_argument('--output-file', default='chapter_1.md', help='Markdown output file')
    p.add_argument('--resize', type=int, default=2000, help='Optional max width to resize images before OCR (px)')
    p.add_argument('--lang', default='eng', help='tesseract language code(s)')
    args = p.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Input directory {input_dir} not found", file=sys.stderr)
        sys.exit(2)

    images = [p for p in sorted(input_dir.iterdir()) if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')]
    if not images:
        print(f"No images found in {input_dir}")
        sys.exit(1)

    pages = []
    for img_path in images:
        print(f"OCR: {img_path.name}")
        text = ocr_image_file(img_path, resize=args.resize, lang=args.lang)

        page_num = extract_page_number_from_text(text)
        pages.append({'file': img_path.name, 'path': str(img_path), 'page': page_num, 'text': text})

    # Determine ordering
    if any(p['page'] is not None for p in pages):
        pages_with = [p for p in pages if p['page'] is not None]
        pages_without = [p for p in pages if p['page'] is None]
        pages_with.sort(key=lambda x: x['page'])
        pages_without.sort(key=lambda x: x['file'])
        ordered = pages_with + pages_without
    else:
        ordered = sorted(pages, key=lambda x: x['file'])

    out_path = Path(args.output_file)
    with out_path.open('w', encoding='utf-8') as f:
        f.write('# Chapter 1\n\n')
        for idx, pinfo in enumerate(ordered, start=1):
            title = f"Page {pinfo['page']}" if pinfo['page'] is not None else f"Page {idx}"
            f.write(f"## {title} — {pinfo['file']}\n\n")
            # write text; strip leading/trailing whitespace but preserve paragraphs
            body = pinfo['text'].strip() if pinfo['text'] else '*[no text extracted]*'
            # Normalize line endings
            body = '\n'.join([line.rstrip() for line in body.splitlines()])
            f.write(body + '\n\n')

    print(f"Wrote markdown to {out_path}")


if __name__ == '__main__':
    main()
