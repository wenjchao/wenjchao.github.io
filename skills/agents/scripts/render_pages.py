#!/usr/bin/env python3
"""Render every page of a PDF to a high-resolution PNG image.

Usage:
    python render_pages.py <paper_dir>/shared/source.pdf <paper_dir>/shared/pages [--dpi 300]

Output:
    <paper_dir>/shared/pages/page_1.png, page_2.png, ...
    Prints JSON list of generated file paths to stdout.
"""
import argparse
import json
import os
import sys

import pypdfium2 as pdfium


def render_pages(pdf_path: str, output_dir: str, dpi: int = 300) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    doc = pdfium.PdfDocument(pdf_path)
    paths = []
    for i in range(len(doc)):
        page = doc[i]
        scale = dpi / 72  # 72 is the default PDF DPI
        bitmap = page.render(scale=scale)
        img = bitmap.to_pil()
        out_path = os.path.join(output_dir, f"page_{i + 1}.png")
        img.save(out_path, "PNG")
        paths.append(out_path)
    doc.close()
    return paths


def main():
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG images")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("output_dir", help="Directory to save rendered pages")
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI (default: 300)")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    paths = render_pages(args.pdf_path, args.output_dir, args.dpi)
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()
