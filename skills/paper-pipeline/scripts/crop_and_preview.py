#!/usr/bin/env python3
"""Crop a figure from a page image and generate all evidence previews in one call.

Combines crop_region.py, make_image_preview.py, and make_edge_previews.py into
a single operation.  Produces: final crop, crop preview, boundary preview,
bottom band segments, and bottom microzoom segments.

Usage:
    python crop_and_preview.py \
        --page-image shared/pages/page_3.png \
        --crop-px 72 120 2410 1850 \
        --crop-id Figure_1 \
        --output-dir <artifact_root>

    Output files:
        <output-dir>/crops/<crop_id>.png
        <output-dir>/previews/<crop_id>_preview.png
        <output-dir>/previews/<crop_id>_boundary_preview.png
        <output-dir>/previews/<crop_id>_{top,left,right}_seg<N>_preview.png
        <output-dir>/previews/<crop_id>_bottom_seg<N>_preview.png
        <output-dir>/previews/<crop_id>_micro_bottom_seg<N>_preview.png
        <output-dir>/boundaries/...  (full-res counterparts)

Outputs a JSON object to stdout listing all generated files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crop figure and generate all evidence previews"
    )
    parser.add_argument("--page-image", required=True,
                        help="Full-resolution page image")
    parser.add_argument("--crop-px", type=int, nargs=4, required=True,
                        metavar=("X1", "Y1", "X2", "Y2"),
                        help="Crop coordinates in page pixels")
    parser.add_argument("--crop-id", required=True,
                        help="Crop ID (used for filenames)")
    parser.add_argument("--output-dir", required=True,
                        help="Artifact root directory")
    parser.add_argument("--max-dim", type=int, default=1568,
                        help="Max preview dimension (default: 1568)")
    parser.add_argument("--band-ratio", type=float, default=1.3,
                        help="Max aspect ratio for bottom band segments (default: 1.3)")
    parser.add_argument("--micro-band", type=int, default=50,
                        help="Microzoom half-width in pixels (default: 50)")
    parser.add_argument("--micro-ratio", type=float, default=4.0,
                        help="Max aspect ratio for microzoom segments (default: 4.0)")
    parser.add_argument("--boundary-only", action="store_true",
                        help="Only produce crop, crop preview, and boundary preview (skip edge strips and microzoom)")
    args = parser.parse_args()

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from crop_region import crop_region
    from make_image_preview import make_preview
    from make_edge_previews import make_edge_previews

    output_dir = Path(args.output_dir)
    crop_id = args.crop_id
    x1, y1, x2, y2 = args.crop_px

    crops_dir = output_dir / "crops"
    previews_dir = output_dir / "previews"
    boundaries_dir = output_dir / "boundaries"
    crops_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)
    boundaries_dir.mkdir(parents=True, exist_ok=True)

    def rel(path: str) -> str:
        return os.path.relpath(path, str(output_dir))

    result: dict = {"crop_id": crop_id, "crop_px": [x1, y1, x2, y2]}

    # 1. Final crop (--padding 0)
    crop_path = str(crops_dir / f"{crop_id}.png")
    crop_region(args.page_image, x1, y1, x2, y2, crop_path, padding=0)
    result["crop_image"] = rel(crop_path)

    # 2. Crop preview
    preview_path = str(previews_dir / f"{crop_id}_preview.png")
    make_preview(Path(crop_path), Path(preview_path), args.max_dim, args.max_dim)

    # 3. Boundary preview (always) + edge band segments (full mode only)
    edge_result_1 = make_edge_previews(
        page_image=args.page_image,
        crop_px=(x1, y1, x2, y2),
        crop_id=crop_id,
        output_dir=str(boundaries_dir),
        preview_dir=str(previews_dir),
        max_ratio=args.band_ratio,
        max_dim=args.max_dim,
        boundary=True,
        band=None,
        edges=[] if args.boundary_only else ["top", "bottom", "left", "right"],
    )

    # 4. Bottom microzoom (full mode only)
    edge_result_2: dict = {}
    if not args.boundary_only:
        edge_result_2 = make_edge_previews(
            page_image=args.page_image,
            crop_px=(x1, y1, x2, y2),
            crop_id=f"{crop_id}_micro",
            output_dir=str(boundaries_dir),
            preview_dir=str(previews_dir),
            max_ratio=args.micro_ratio,
            max_dim=args.max_dim,
            boundary=False,
            band=args.micro_band,
            edges=["bottom"],
        )

    # Build previews dict with relative paths
    result["previews"] = {
        "crop": rel(preview_path),
        "boundary": rel(edge_result_1.get("boundary", {}).get("preview", "")),
    }
    if not args.boundary_only:
        result["previews"].update({
            "top": [rel(seg["preview"]) for seg in edge_result_1.get("top", {}).get("segments", [])],
            "left": [rel(seg["preview"]) for seg in edge_result_1.get("left", {}).get("segments", [])],
            "right": [rel(seg["preview"]) for seg in edge_result_1.get("right", {}).get("segments", [])],
            "bottom_band": [rel(seg["preview"]) for seg in edge_result_1.get("bottom", {}).get("segments", [])],
            "bottom_micro": [rel(seg["preview"]) for seg in edge_result_2.get("bottom", {}).get("segments", [])],
        })

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
