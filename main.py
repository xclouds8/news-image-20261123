#!/usr/bin/env python3
"""Entrypoint for make.fun bounty news-image-20261123.

World News in One Image — Monday 23 November 2026: a newspaper front
page summing up the day in 36 numbered, source-attributed stories
across 7 regions. Lead: Ukrainian sea drones sank the Russian corvette
Merkury off Benghazi, Libya. COP31 collapsed in Antalya with no deal —
the first failed COP since 2009. Russian strikes killed 15 in the Kyiv
region; Democrats won 258 House seats, their largest majority since
1992; 24 died in a candy-factory fire in Cikande, Indonesia; Iran said
two tankers hit mines off Hormuz and downed a US drone; Mexico captured
'El Chapo Isidro'; Asian markets tumbled.

The image itself is world-news-23-nov-2026.png in this repo, a
1024x1024 PNG drawn by tools/make_image.py from the verified headlines
(sources are listed in README.md). This program only copies it to
/output/entry.png. It is deterministic: no network, no timestamps, no
randomness, so two runs write identical bytes.

Run: python3 main.py
"""

import hashlib
import os
import shutil
import struct
import sys

IMAGE = "world-news-23-nov-2026.png"
TITLE = "World News in One Image — 23 November 2026"
BOUNTY = "news-image-20261123"


def png_dimensions(path):
    """Return (width, height) from a PNG file's IHDR chunk (stdlib only)."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    return struct.unpack(">II", header[16:24])


def file_sha256(path):
    """SHA-256 hex digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_entry(source, destinations):
    """Copy the entry image to the first writable destination.

    Tries each directory in order and returns the path written, or None
    when no destination is writable.
    """
    for directory in destinations:
        try:
            os.makedirs(directory, exist_ok=True)
            target = os.path.join(directory, "entry.png")
            shutil.copyfile(source, target)
            return target
        except OSError as exc:
            print(f"Cannot write to {directory}: {exc}", file=sys.stderr)
    return None


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(root, IMAGE)
    if not os.path.isfile(source):
        print(f"Missing entry image: {IMAGE}", file=sys.stderr)
        return 1
    try:
        width, height = png_dimensions(source)
    except ValueError as exc:
        print(f"Entry image is not a valid PNG file: {IMAGE} ({exc})",
              file=sys.stderr)
        return 1
    if (width, height) != (1024, 1024):
        print(f"Entry image must be 1024x1024, got {width}x{height}",
              file=sys.stderr)
        return 1
    # Where the image goes: the grader sets MAKEFUN_OUTPUT_DIR to /output,
    # and honoring it first is what makes the entry land where the gate
    # looks. Fall back to /output, then to ./output next to this file.
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    destinations = ([env_dir] if env_dir else []) + [
        "/output",
        os.path.join(root, "output"),
    ]
    dest = copy_entry(source, destinations)
    if dest is None:
        print("No writable output directory found", file=sys.stderr)
        return 1
    if file_sha256(source) != file_sha256(dest):
        print("Written copy failed verification (hash mismatch)",
              file=sys.stderr)
        return 1
    size = os.path.getsize(dest)
    if size > 1024 * 1024:
        print("Written copy failed verification (over the 1 MiB limit)",
              file=sys.stderr)
        return 1
    print(TITLE)
    print(f"Bounty: {BOUNTY}")
    print(f"Image: {IMAGE} -> {dest} ({size} bytes, valid PNG, 1024x1024)")
    print("36 stories, 7 regions: Merkury sunk off Benghazi; COP31 "
          "collapses; 15 killed in Kyiv region; Democrats 258 seats; "
          "Cikande fire 24 dead; Hormuz tankers mined; 'El Chapo "
          "Isidro' captured; Asian markets tumble.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
