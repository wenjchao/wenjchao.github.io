#!/usr/bin/env python3
"""Render a structured Table_N.json into a visual preview image.

Usage:
    python render_table_preview.py Table_1.json rendered_tables/Table_1_rendered.png
"""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def render_table(data: dict, output_path: str, max_width: int = 1600) -> str:
    """Render structured table JSON to a PNG preview."""
    # Extract fields
    table_id = data.get("table_id", "")
    table_label = data.get("table_label", "")
    table_title = data.get("table_title", "")
    headers = data.get("headers")
    header_levels = data.get("header_levels")
    rows = data.get("rows", [])
    footnotes = data.get("footnotes", [])

    # Build header rows
    header_rows = []
    if header_levels:
        header_rows = header_levels
    elif headers:
        header_rows = [headers]

    # Determine column count
    if header_rows:
        col_count = max(len(r) for r in header_rows)
    elif rows:
        col_count = max(len(r) for r in rows)
    else:
        col_count = 1

    # Try to load a monospace font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        except Exception:
            font = ImageFont.load_default()

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    except Exception:
        title_font = font

    padding = 6
    cell_padding = 4

    # Measure column widths
    col_widths = [60] * col_count
    all_rows = header_rows + rows

    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    for row in all_rows:
        for ci, cell in enumerate(row):
            if ci >= col_count:
                break
            text = str(cell) if cell is not None else ""
            bbox = dummy_draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0] + cell_padding * 2
            col_widths[ci] = max(col_widths[ci], tw)

    # Cap total width
    total_width = sum(col_widths) + padding * 2
    if total_width > max_width:
        scale = max_width / total_width
        col_widths = [max(30, int(w * scale)) for w in col_widths]
        total_width = sum(col_widths) + padding * 2

    row_height = 24
    title_height = 40 if table_title else 0
    header_height = len(header_rows) * row_height
    body_height = len(rows) * row_height
    footnote_height = len(footnotes) * row_height if footnotes else 0

    img_height = title_height + header_height + body_height + footnote_height + padding * 4 + 20
    img_width = total_width

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    y = padding

    # Draw title
    if table_title:
        draw.text((padding, y), table_title, fill="black", font=title_font)
        y += title_height

    # Draw header rows
    for hi, hrow in enumerate(header_rows):
        x = padding
        for ci in range(col_count):
            cell_text = str(hrow[ci]) if ci < len(hrow) else ""
            draw.rectangle([x, y, x + col_widths[ci], y + row_height], outline="#888888", fill="#E0E0E0")
            draw.text((x + cell_padding, y + 4), cell_text, fill="black", font=font)
            x += col_widths[ci]
        y += row_height

    # Draw separator
    draw.line([(padding, y), (img_width - padding, y)], fill="black", width=2)

    # Draw data rows
    for ri, row in enumerate(rows):
        x = padding
        bg = "#FFFFFF" if ri % 2 == 0 else "#F5F5F5"
        for ci in range(col_count):
            cell_text = str(row[ci]) if ci < len(row) else ""
            draw.rectangle([x, y, x + col_widths[ci], y + row_height], outline="#CCCCCC", fill=bg)
            draw.text((x + cell_padding, y + 4), cell_text, fill="black", font=font)
            x += col_widths[ci]
        y += row_height

    # Draw footnotes
    if footnotes:
        y += 8
        draw.line([(padding, y), (img_width // 3, y)], fill="#888888", width=1)
        y += 4
        for fn in footnotes:
            draw.text((padding, y), str(fn), fill="#444444", font=font)
            y += row_height

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render structured Table JSON to preview image")
    parser.add_argument("input_json", help="Path to Table_N.json")
    parser.add_argument("output_image", help="Output PNG path")
    parser.add_argument("--max-width", type=int, default=1600)
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = render_table(data, args.output_image, args.max_width)
    print(f"Rendered: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
