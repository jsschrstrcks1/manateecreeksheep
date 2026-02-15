#!/usr/bin/env python3
"""
Process oversized sheep images for AI reading.

All original images in the repository are >2000px (typically 4032x3024 for JPGs,
1320x2868 for PNGs). Claude's API rejects images over 2000px.

This script creates processed versions at ≤1800px in data/processed/.
"""

import os
import sys
import json
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

# Configuration
MAX_DIMENSION = 1800
QUALITY = 85
REPO_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


def get_image_files():
    """Find all image files in the repository root."""
    files = []
    for f in REPO_ROOT.iterdir():
        if f.suffix in IMAGE_EXTENSIONS and f.is_file():
            files.append(f)
    return sorted(files)


def needs_processing(src: Path, dst: Path) -> bool:
    """Check if an image needs to be processed."""
    if not dst.exists():
        return True
    if src.stat().st_mtime > dst.stat().st_mtime:
        return True
    return False


def process_image(src: Path, dst: Path) -> dict:
    """Process a single image. Returns status dict."""
    try:
        img = Image.open(src)
        w, h = img.size
        original_size = f"{w}x{h}"

        # Calculate resize ratio
        ratio = min(MAX_DIMENSION / w, MAX_DIMENSION / h)
        if ratio < 1:
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            new_size = f"{new_w}x{new_h}"
        else:
            new_size = original_size

        # Convert to RGB (handles RGBA PNGs) and save as JPEG
        img = img.convert("RGB")
        img.save(dst, "JPEG", quality=QUALITY)

        return {
            "source": src.name,
            "processed": dst.name,
            "original_size": original_size,
            "processed_size": new_size,
            "status": "processed"
        }
    except Exception as e:
        return {
            "source": src.name,
            "status": "error",
            "error": str(e)
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process sheep images for AI reading")
    parser.add_argument("--status", action="store_true", help="Show status without processing")
    parser.add_argument("--file", type=str, help="Process a single file")
    parser.add_argument("--force", action="store_true", help="Reprocess all images")
    args = parser.parse_args()

    # Ensure processed directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if args.file:
        src = REPO_ROOT / args.file
        if not src.exists():
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)
        dst = PROCESSED_DIR / (src.stem + ".jpeg")
        result = process_image(src, dst)
        print(f"{result['source']}: {result['status']}")
        if result['status'] == 'processed':
            print(f"  {result['original_size']} -> {result['processed_size']}")
        return

    files = get_image_files()
    if not files:
        print("No image files found in repository root.")
        return

    if args.status:
        print(f"Found {len(files)} images in repository root:\n")
        processed = 0
        oversized = 0
        for f in files:
            dst = PROCESSED_DIR / (f.stem + ".jpeg")
            img = Image.open(f)
            w, h = img.size
            is_oversized = max(w, h) > 2000
            has_processed = dst.exists()

            status = "OK" if has_processed else ("NEEDS PROCESSING" if is_oversized else "OK (small)")
            if is_oversized:
                oversized += 1
            if has_processed:
                processed += 1

            print(f"  {f.name}: {w}x{h} [{status}]")

        print(f"\nTotal: {len(files)} images, {oversized} oversized, {processed} processed")
        return

    # Process all images
    results = []
    for f in files:
        dst = PROCESSED_DIR / (f.stem + ".jpeg")
        if not args.force and not needs_processing(f, dst):
            print(f"  {f.name}: already processed (skip)")
            continue

        result = process_image(f, dst)
        results.append(result)

        if result['status'] == 'processed':
            print(f"  {f.name}: {result['original_size']} -> {result['processed_size']}")
        else:
            print(f"  {f.name}: ERROR - {result.get('error', 'unknown')}")

    processed = sum(1 for r in results if r['status'] == 'processed')
    errors = sum(1 for r in results if r['status'] == 'error')
    print(f"\nProcessed: {processed}, Errors: {errors}, Skipped: {len(files) - len(results)}")


if __name__ == "__main__":
    main()
