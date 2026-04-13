#!/usr/bin/env python3
"""
assign_posters.py

Copy uploaded poster images from an `uploads/` folder into `app/static/img/` using
a predictable naming scheme so the site can display them on the homepage.

Usage:
  python scripts/assign_posters.py [uploads_dir]

Place your uploaded images (the ones you attached) into the `uploads/` folder
at the workspace root, then run this script. Files are copied in alphanumeric
order and assigned to featured/trending/upcoming/premium slots.
"""
import sys
import os
import shutil
from pathlib import Path

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def gather_images(src_dir):
    p = Path(src_dir)
    if not p.exists():
        print(f'Uploads directory not found: {src_dir}')
        return []
    files = [f for f in sorted(p.iterdir()) if f.suffix.lower() in SUPPORTED and f.is_file()]
    return files

def copy_with_index(files, dest_dir, prefix, count):
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    mapping = []
    for i in range(count):
        if not files:
            break
        src = files.pop(0)
        dest = dest_dir / f"{prefix}-{i+1}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        mapping.append((src.name, dest.name))
    return mapping

def main():
    uploads = sys.argv[1] if len(sys.argv) > 1 else 'uploads'
    files = gather_images(uploads)
    if not files:
        print('No images found in', uploads)
        return

    dest = Path('app') / 'static' / 'img'
    # counts can be adjusted
    featured_count = 6
    trending_count = 8
    upcoming_count = 6
    premium_count = 12

    all_files = list(files)
    print(f'Found {len(all_files)} images, assigning...')

    mapping = {}
    mapping['featured'] = copy_with_index(all_files, dest, 'featured', featured_count)
    mapping['trending'] = copy_with_index(all_files, dest, 'trending', trending_count)
    mapping['upcoming'] = copy_with_index(all_files, dest, 'upcoming', upcoming_count)
    mapping['premium'] = copy_with_index(all_files, dest, 'premium', premium_count)

    print('\nMapping:')
    for k, v in mapping.items():
        if v:
            print(f' {k}:')
            for src, dst in v:
                print(f'   {src} -> {dst}')

    if all_files:
        print('\nUnassigned images:')
        for f in all_files:
            print('  ', f.name)

    print('\nDone. Restart your dev server if it is running to pick up new static files.')

if __name__ == '__main__':
    main()
