#!/usr/bin/env python3
"""Crop a rectangular region from a rendered page image.

Usage:
    python crop_region.py <image_path> <x1> <y1> <x2> <y2> <output_path> [--padding 5]
    python crop_region.py <image_path> <x1> <y1> <x2> <y2> <output_path> --hline 1565 --vline 250

Coordinates are in pixels (from rendered page image).
(x1, y1) = top-left corner, (x2, y2) = bottom-right corner.

Optional --padding adds N pixels of whitespace around the crop for cleanliness.
Optional --hline/--vline draws boundary lines at source-image coordinates.
"""
import argparse
import os
import sys
from typing import Optional

from PIL import Image, ImageDraw


def crop_region(image_path: str, x1: int, y1: int, x2: int, y2: int,
                output_path: str, padding: int = 5,
                hlines: Optional[list[int]] = None,
                vlines: Optional[list[int]] = None,
                line_color: tuple[int, int, int] = (0, 200, 200),
                line_width: int = 4) -> str:
    img = Image.open(image_path)
    w, h = img.size

    # Apply padding (expand crop box, clamp to image bounds)
    orig_x1, orig_y1, orig_x2, orig_y2 = x1 - padding, y1 - padding, x2 + padding, y2 + padding
    cx1 = max(0, orig_x1)
    cy1 = max(0, orig_y1)
    cx2 = min(w, orig_x2)
    cy2 = min(h, orig_y2)

    if (cx1 != orig_x1 or cy1 != orig_y1 or cx2 != orig_x2 or cy2 != orig_y2):
        print(f"Warning: coordinates clamped from [{orig_x1},{orig_y1},{orig_x2},{orig_y2}] "
              f"to [{cx1},{cy1},{cx2},{cy2}] (image size {w}x{h})", file=sys.stderr)

    cropped = img.crop((cx1, cy1, cx2, cy2))

    if hlines or vlines:
        draw = ImageDraw.Draw(cropped)
        cw, ch = cropped.size
        for src_y in (hlines or []):
            local_y = src_y - cy1
            if 0 <= local_y < ch:
                draw.line([(0, local_y), (cw - 1, local_y)],
                          fill=line_color, width=line_width)
        for src_x in (vlines or []):
            local_x = src_x - cx1
            if 0 <= local_x < cw:
                draw.line([(local_x, 0), (local_x, ch - 1)],
                          fill=line_color, width=line_width)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cropped.save(output_path, "PNG")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Crop a region from an image")
    parser.add_argument("image_path", help="Source image path")
    parser.add_argument("x1", type=int, help="Left edge (pixels)")
    parser.add_argument("y1", type=int, help="Top edge (pixels)")
    parser.add_argument("x2", type=int, help="Right edge (pixels)")
    parser.add_argument("y2", type=int, help="Bottom edge (pixels)")
    parser.add_argument("output_path", help="Output cropped image path")
    parser.add_argument("--padding", type=int, default=5,
                        help="Pixels of padding around crop (default: 5)")
    parser.add_argument("--hline", type=int, action="append", default=[],
                        help="Draw horizontal boundary line at this source-image Y (repeatable)")
    parser.add_argument("--vline", type=int, action="append", default=[],
                        help="Draw vertical boundary line at this source-image X (repeatable)")
    parser.add_argument("--line-color", default="0,200,200",
                        help="Boundary line RGB color (default: 0,200,200 cyan)")
    parser.add_argument("--line-width", type=int, default=4,
                        help="Boundary line width in pixels (default: 4)")
    args = parser.parse_args()

    line_color = tuple(int(c) for c in args.line_color.split(","))

    result = crop_region(args.image_path, args.x1, args.y1, args.x2, args.y2,
                         args.output_path, args.padding,
                         hlines=args.hline or None,
                         vlines=args.vline or None,
                         line_color=line_color,
                         line_width=args.line_width)
    print(f"Cropped: {result}")


if __name__ == "__main__":
    main()
