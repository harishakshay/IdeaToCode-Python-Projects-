	#!/usr/bin/env python3
"""
FileOrganizer: automatically sort files by type and modification date.
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
import mimetypes

def categorize_file(file_path: Path) -> str:
    """Return a category folder name based on mime type."""
    mime, _ = mimetypes.guess_type(file_path.name)
    if not mime:
        return "Others"
    main_type = mime.split('/')[0]
    mapping = {
        "image": "Images",
        "video": "Videos",
        "audio": "Audio",
        "text": "Documents",
        "application": "Applications",
    }
    return mapping.get(main_type, "Others")

def safe_move(src: Path, dst: Path):
    """Move src to dst, renaming if a conflict exists."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        stem = dst.stem
        suffix = dst.suffix
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_dst = dst.with_name(new_name)
            if not new_dst.exists():
                dst = new_dst
                break
            counter += 1
    shutil.move(str(src), str(dst))

def organize(src_dir: Path, dst_dir: Path, by_type: bool, by_date: bool, dry_run: bool):
    """Iterate over files in src_dir and move them to dst_dir based on criteria."""
    for item in src_dir.iterdir():
        if item.is_file():
            parts = []
            if by_type:
                parts.append(categorize_file(item))
            if by_date:
                mod_time = datetime.fromtimestamp(item.stat().st_mtime)
                parts.append(mod_time.strftime("%Y-%m-%d"))
            target_dir = dst_dir.joinpath(*parts) if parts else dst_dir
            target_path = target_dir / item.name
            if dry_run:
                print(f"[DRY-RUN] Would move: {item} -> {target_path}")
            else:
                safe_move(item, target_path)
                print(f"Moved: {item} -> {target_path}")

def parse_args():
    parser = argparse.ArgumentParser(description="Organize files by type and modification date.")
    parser.add_argument("source", nargs="?", default=".", help="Source directory (default: current).")
    parser.add_argument("destination", nargs="?", default="./organized", help="Destination directory.")
    parser.add_argument("--no-type", action="store_true", help="Do not organize by file type.")
    parser.add_argument("--no-date", action="store_true", help="Do not organize by modification date.")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without moving files.")
    return parser.parse_args()

def main():
    args = parse_args()
    src = Path(args.source).resolve()
    dst = Path(args.destination).resolve()
    if not src.is_dir():
        print(f"Error: source '{src}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    dst.mkdir(parents=True, exist_ok=True)
    organize(
        src_dir=src,
        dst_dir=dst,
        by_type=not args.no_type,
        by_date=not args.no_date,
        dry_run=args.dry_run,
    )

if __name__ == "__main__":
    main()
