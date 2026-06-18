#!/usr/bin/env python3
"""Create a bounded-size preview image for model inspection."""

import argparse
import json
from pathlib import Path

from PIL import Image


def make_preview(input_path: Path, output_path: Path, max_width: int, max_height: int) -> dict:
    image = Image.open(input_path).convert("RGB")
    original_size = image.size
    preview = image.copy()
    preview.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    preview.save(output_path)
    scale_x = preview.size[0] / original_size[0]
    scale_y = preview.size[1] / original_size[1]
    return {
        "input": str(input_path),
        "output": str(output_path),
        "original_size": list(original_size),
        "preview_size": list(preview.size),
        "scale_x": scale_x,
        "scale_y": scale_y,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a preview image with bounded dimensions.")
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    parser.add_argument("--max-width", type=int, default=1568)
    parser.add_argument("--max-height", type=int, default=1568)
    parser.add_argument("--max-dim", type=int, help="Set both max-width and max-height to the same value")
    args = parser.parse_args()

    if args.max_dim:
        args.max_width = args.max_dim
        args.max_height = args.max_dim

    result = make_preview(
        Path(args.input_path),
        Path(args.output_path),
        args.max_width,
        args.max_height,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
