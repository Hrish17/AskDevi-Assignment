#!/usr/bin/env python3
"""
Script to preprocess and chunk the Brihat Parashara Hora Shastra (BPHS) text into ~500-700 character segments,
tagging each chunk with chapter metadata, and outputting a JSON file.
"""

import argparse
import json
import re


def chunk_text(text, size=600):
    """
    Split `text` into chunks of up to `size` characters, trying to end at sentence boundaries.
    """
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + size, length)
        if end < length:
            # Prefer to end at the last period before `end`
            period = text.rfind('.', start, end)
            if period != -1 and period > start:
                end = period + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Chunk BPHS text into JSON segments with metadata"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to the input BPHS text file (plain .txt)"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Path for the output JSON file of chunks"
    )
    parser.add_argument(
        "--size", "-s", type=int, default=600,
        help="Approximate chunk size in characters (default: 600)"
    )
    args = parser.parse_args()

    # Read full BPHS text
    with open(args.input, 'r', encoding='utf-8') as f:
        full_text = f.read()

    # Updated: Split by lines starting with 'Ch.' to capture chapter headings
    chapter_pattern = r'^(Ch\.?\s*\d+\.?\s*\.?\s*.*)$'
    parts = re.split(chapter_pattern, full_text, flags=re.MULTILINE)

    chunks = []
    current_chapter = "Introduction"
    chunk_id = 1

    for part in parts:
        if re.match(chapter_pattern, part, flags=re.MULTILINE):
            current_chapter = part.strip()
        else:
            # Generate sub-chunks for this chapter section
            for ct in chunk_text(part, size=args.size):
                chunks.append({
                    "chunk_id": f"BPHS-{current_chapter.replace(' ', '_')}-{chunk_id}",
                    "chapter": current_chapter,
                    "content": ct
                })
                chunk_id += 1

    # Write to JSON
    with open(args.output, 'w', encoding='utf-8') as out:
        json.dump(chunks, out, ensure_ascii=False, indent=2)

    print(f"Generated {len(chunks)} chunks and saved to {args.output}")


if __name__ == '__main__':
    main()
