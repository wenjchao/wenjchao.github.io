#!/usr/bin/env python3
"""Generate segmented edge strip previews (and optionally boundary preview) for a crop unit.

Centralises the margin / edge-band geometry that was previously hand-calculated
in three separate subagent prompts.  Each edge is split into segments when the
natural aspect ratio exceeds --max-ratio, guaranteeing that small text near the
boundary line is legible in the preview.

Usage:
    python make_edge_previews.py \
        --page-image shared/pages/page_3.png \
        --crop-px 80 1195 2405 2880 \
        --crop-id Figure_3 \
        --output-dir figures/workers/worker_01/boundaries \
        --preview-dir figures/workers/worker_01/previews \
        --max-ratio 1.3 \
        --boundary

Outputs a JSON object to stdout describing every generated file.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import struct
import sys
from pathlib import Path

EDGES = ("top", "bottom", "left", "right")
OVERLAP_FRAC = 0.15


def read_png_size(path: str) -> tuple[int, int]:
    with open(path, "rb") as fh:
        header = fh.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"Cannot read PNG header: {path}")
    width, height = struct.unpack(">II", header[16:24])
    return int(width), int(height)


def run_crop(page_image: str, x1: int, y1: int, x2: int, y2: int,
             output: str, hlines: list[int] | None = None,
             vlines: list[int] | None = None) -> None:
    from crop_region import crop_region
    crop_region(page_image, x1, y1, x2, y2, output, padding=0,
                hlines=hlines, vlines=vlines)


def run_preview(input_path: str, output_path: str, max_dim: int) -> None:
    from make_image_preview import make_preview
    make_preview(Path(input_path), Path(output_path), max_dim, max_dim)


def clamp(val: int, lo: int, hi: int) -> int:
    return max(lo, min(val, hi))


def compute_segments(edge_length: int, band_height: int, max_ratio: float) -> list[tuple[int, int]]:
    """Return list of (start, end) offsets along the edge parallel axis.

    max_ratio caps the aspect ratio of each segment *after* overlap is added.
    We work backwards: each segment's visible (non-overlapping) width is
    band_height * max_ratio * (1 - OVERLAP_FRAC), so the final segment
    including overlap on both sides stays within max_ratio.
    """
    if edge_length <= 0 or band_height <= 0:
        return [(0, edge_length)]
    effective_width = band_height * max_ratio * (1 - OVERLAP_FRAC)
    if effective_width <= 0:
        return [(0, edge_length)]
    n = math.ceil(edge_length / effective_width)
    if n <= 1:
        return [(0, edge_length)]
    stride = edge_length / n
    overlap = round(OVERLAP_FRAC * stride)
    segments = []
    for i in range(n):
        seg_start = max(0, round(i * stride) - overlap)
        seg_end = min(edge_length, round((i + 1) * stride) + overlap)
        segments.append((seg_start, seg_end))
    return segments


def make_edge_previews(
    page_image: str,
    crop_px: tuple[int, int, int, int],
    crop_id: str,
    output_dir: str,
    preview_dir: str,
    max_ratio: float = 1.3,
    max_dim: int = 1568,
    boundary: bool = False,
    band: int | None = None,
    edges: list[str] | None = None,
) -> dict:
    cx1, cy1, cx2, cy2 = crop_px
    crop_w = cx2 - cx1
    crop_h = cy2 - cy1
    page_w, page_h = read_png_size(page_image)

    if band is not None:
        edge_band_y = band
        edge_band_x = band
    else:
        edge_band_y = max(round(0.12 * crop_h), 160)
        edge_band_x = max(round(0.12 * crop_w), 160)

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    result: dict = {}

    if boundary:
        margin_y = max(round(0.15 * crop_h), 250)
        margin_x = max(round(0.15 * crop_w), 250)
        bx1 = clamp(cx1 - margin_x, 0, page_w)
        by1 = clamp(cy1 - margin_y, 0, page_h)
        bx2 = clamp(cx2 + margin_x, 0, page_w)
        by2 = clamp(cy2 + margin_y, 0, page_h)

        bnd_img = os.path.join(output_dir, f"{crop_id}.png")
        bnd_prev = os.path.join(preview_dir, f"{crop_id}_boundary_preview.png")
        run_crop(page_image, bx1, by1, bx2, by2, bnd_img,
                 hlines=[cy1, cy2], vlines=[cx1, cx2])
        run_preview(bnd_img, bnd_prev, max_dim)
        result["boundary"] = {
            "boundary_image": bnd_img,
            "preview": bnd_prev,
            "source_coords": [bx1, by1, bx2, by2],
        }

    edge_specs: dict[str, dict] = {
        "top": {
            "parallel_origin": cx1,
            "parallel_length": crop_w,
            "perp_lo": clamp(cy1 - edge_band_y, 0, page_h),
            "perp_hi": clamp(cy1 + edge_band_y, 0, page_h),
            "band_height": clamp(cy1 + edge_band_y, 0, page_h) - clamp(cy1 - edge_band_y, 0, page_h),
            "hlines": [cy1],
            "vlines": None,
            "is_horizontal": True,
        },
        "bottom": {
            "parallel_origin": cx1,
            "parallel_length": crop_w,
            "perp_lo": clamp(cy2 - edge_band_y, 0, page_h),
            "perp_hi": clamp(cy2 + edge_band_y, 0, page_h),
            "band_height": clamp(cy2 + edge_band_y, 0, page_h) - clamp(cy2 - edge_band_y, 0, page_h),
            "hlines": [cy2],
            "vlines": None,
            "is_horizontal": True,
        },
        "left": {
            "parallel_origin": cy1,
            "parallel_length": crop_h,
            "perp_lo": clamp(cx1 - edge_band_x, 0, page_w),
            "perp_hi": clamp(cx1 + edge_band_x, 0, page_w),
            "band_height": clamp(cx1 + edge_band_x, 0, page_w) - clamp(cx1 - edge_band_x, 0, page_w),
            "hlines": None,
            "vlines": [cx1],
            "is_horizontal": False,
        },
        "right": {
            "parallel_origin": cy1,
            "parallel_length": crop_h,
            "perp_lo": clamp(cx2 - edge_band_x, 0, page_w),
            "perp_hi": clamp(cx2 + edge_band_x, 0, page_w),
            "band_height": clamp(cx2 + edge_band_x, 0, page_w) - clamp(cx2 - edge_band_x, 0, page_w),
            "hlines": None,
            "vlines": [cx2],
            "is_horizontal": False,
        },
    }

    active_edges = edges if edges else list(EDGES)
    for edge in active_edges:
        spec = edge_specs[edge]
        segments = compute_segments(
            spec["parallel_length"], spec["band_height"], max_ratio
        )

        for stale in glob.glob(os.path.join(output_dir, f"{crop_id}_{edge}_seg*")):
            os.remove(stale)
        for stale in glob.glob(os.path.join(preview_dir, f"{crop_id}_{edge}_seg*")):
            os.remove(stale)

        seg_results = []
        for seg_idx, (seg_start, seg_end) in enumerate(segments, start=1):
            seg_label = f"seg{seg_idx}"
            fname_base = f"{crop_id}_{edge}_{seg_label}"

            if spec["is_horizontal"]:
                sx1 = spec["parallel_origin"] + seg_start
                sx2 = spec["parallel_origin"] + seg_end
                sy1 = spec["perp_lo"]
                sy2 = spec["perp_hi"]
            else:
                sx1 = spec["perp_lo"]
                sx2 = spec["perp_hi"]
                sy1 = spec["parallel_origin"] + seg_start
                sy2 = spec["parallel_origin"] + seg_end

            sx1 = clamp(sx1, 0, page_w)
            sx2 = clamp(sx2, 0, page_w)
            sy1 = clamp(sy1, 0, page_h)
            sy2 = clamp(sy2, 0, page_h)

            strip_img = os.path.join(output_dir, f"{fname_base}.png")
            strip_prev = os.path.join(preview_dir, f"{fname_base}_preview.png")

            run_crop(page_image, sx1, sy1, sx2, sy2, strip_img,
                     hlines=spec["hlines"], vlines=spec["vlines"])
            run_preview(strip_img, strip_prev, max_dim)

            seg_results.append({
                "boundary_image": strip_img,
                "preview": strip_prev,
                "source_coords": [sx1, sy1, sx2, sy2],
            })

        result[edge] = {"segments": seg_results}

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate segmented edge strip previews for a crop unit."
    )
    parser.add_argument("--page-image", required=True)
    parser.add_argument("--crop-px", type=int, nargs=4, required=True,
                        metavar=("X1", "Y1", "X2", "Y2"))
    parser.add_argument("--crop-id", required=True)
    parser.add_argument("--output-dir", required=True,
                        help="Directory for full-res boundary/edge strip images")
    parser.add_argument("--preview-dir", required=True,
                        help="Directory for preview images")
    parser.add_argument("--max-ratio", type=float, default=1.5,
                        help="Max aspect ratio per segment after overlap (default: 1.3)")
    parser.add_argument("--max-dim", type=int, default=1568,
                        help="Max preview dimension (default: 1568)")
    parser.add_argument("--boundary", action="store_true",
                        help="Also generate boundary image + preview")
    parser.add_argument("--band", type=int, default=None,
                        help="Override edge band (px each side of boundary). "
                             "Use --band 50 for microzoom mode.")
    parser.add_argument("--edges", nargs="+", choices=EDGES, default=None,
                        help="Only generate these edges (default: all four)")
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    result = make_edge_previews(
        page_image=args.page_image,
        crop_px=tuple(args.crop_px),
        crop_id=args.crop_id,
        output_dir=args.output_dir,
        preview_dir=args.preview_dir,
        max_ratio=args.max_ratio,
        max_dim=args.max_dim,
        boundary=args.boundary,
        band=args.band,
        edges=args.edges,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
