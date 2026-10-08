"""Turn a screen recording (.mp4) into a small GIF.

Usage: python -m tools.video_to_gif input.mp4 docs/m1_demo.gif [--width 800] [--fps 15] [--start 0] [--seconds 10]

A GIF can only hold 256 colours. Small saturated objects (like our coloured cubes)
cover few pixels, so a naive palette drops them and the colours turn pale. We build
ONE palette from sampled frames using MAXCOVERAGE (which keeps outlier colours),
and map every frame to it without dithering. This also makes the file much smaller.
"""
import argparse

import cv2
from PIL import Image

PALETTE_SAMPLES = 12


def read_frames(path: str, width: int, fps: int, start: float, seconds: float):
    """Yield resized RGB frames, keeping about `fps` of them per second."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open {path}")
    source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(source_fps / fps, 1.0)               # keep every `step`-th source frame
    last = (start + seconds) * source_fps
    index, next_keep = 0, start * source_fps
    while index <= last:
        ok, frame = cap.read()
        if not ok:
            break
        if index >= next_keep:
            height = int(frame.shape[0] * width / frame.shape[1])
            small = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            yield Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
            next_keep += step
        index += 1
    cap.release()


def build_palette(samples: list) -> Image.Image:
    """Stack the sample frames into one tall image and quantize that."""
    width, height = samples[0].size
    montage = Image.new("RGB", (width, height * len(samples)))
    for i, image in enumerate(samples):
        montage.paste(image, (0, i * height))
    return montage.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--width", type=int, default=800, help="output width in pixels")
    parser.add_argument("--fps", type=int, default=15, help="GIF frames per second")
    parser.add_argument("--start", type=float, default=0.0, help="start time in seconds")
    parser.add_argument("--seconds", type=float, default=10.0, help="how much to keep")
    args = parser.parse_args()
    settings = (args.input, args.width, args.fps, args.start, args.seconds)

    # Pass 1: keep only a handful of frames, just to build the palette.
    all_frames = list(read_frames(*settings))
    if not all_frames:
        raise SystemExit("No frames read; check --start and --seconds")
    every = max(len(all_frames) // PALETTE_SAMPLES, 1)
    palette = build_palette(all_frames[::every])

    # Pass 2: map every frame onto that one palette, without dithering.
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in all_frames]
    frames[0].save(
        args.output, save_all=True, append_images=frames[1:],
        duration=int(1000 / args.fps), loop=0, optimize=True,
    )
    print(f"Wrote {args.output}: {len(frames)} frames at {args.fps} fps")


if __name__ == "__main__":
    main()
