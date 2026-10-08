#Record a few seconds of one joint, then compare One Euro filter settings on it.

#Hold still for the first ~2.5 s (measures jitter at rest), then wave that joint
#quickly (measures lag). Runs without opening a camera window.

#Usage: python -m tools.plot_smoothing [--seconds 8] [--joint right_wrist]
 #      python -m tools.plot_smoothing --replay data/smoothing_recording.npz
#
import argparse
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw to a file, no window
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from perception.camera import open_camera  # noqa: E402
from perception.filters import OneEuroFilter  # noqa: E402
from perception.pose import MediaPipePose  # noqa: E402
from perception.skeleton import LANDMARK_NAMES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RECORDING = ROOT / "data" / "smoothing_recording.npz"
OUTPUT = ROOT / "docs" / "smoothing.png"

IMAGE_WIDTH = 640         # to report jitter in pixels
STILL_WINDOW_SECONDS = 1.0  # jitter is measured in the stillest 1-second stretch found
MOVE_START = 3.0          # waving is assumed to start after this

# (min_cutoff, beta): edit these to experiment.
SETTINGS = [(1.0, 0.0), (1.0, 4.0), (0.3, 4.0)]


def record(seconds: float) -> tuple[np.ndarray, np.ndarray]:
    pose = MediaPipePose()
    cap = open_camera()
    times, frames = [], []
    start = time.perf_counter()
    announced = set()
    print("Get in view. Recording starts now.")
    try:
        while (now := time.perf_counter() - start) < seconds:
            ok, frame = cap.read()
            if not ok:
                break
            if now < 0.3 and "still" not in announced:
                announced.add("still")
                print(">>> HOLD STILL (about 2.5 seconds)")
            if now >= 2.5 and "move" not in announced:
                announced.add("move")
                print(">>> NOW WAVE THE JOINT FAST")
            joints = pose.process(frame, int(now * 1000))
            if joints is not None:
                times.append(now)
                frames.append(joints)
    finally:
        pose.close()
        cap.release()
    return np.array(times), np.array(frames)


def stillest_window(t: np.ndarray, raw: np.ndarray) -> slice:
    """The 1-second stretch where the raw signal moves least (smallest frame-to-frame steps).

    Searching for it is safer than assuming "the first 2 seconds were still".
    """
    n = max(int(STILL_WINDOW_SECONDS / np.median(np.diff(t))), 5)
    steps = np.abs(np.diff(raw))
    start = min(range(len(steps) - n + 1), key=lambda i: steps[i:i + n].mean())
    return slice(start, start + n + 1)


def jitter_px(x: np.ndarray, window: slice) -> float:
    """Typical size of one frame-to-frame step (root mean square), in pixels.

    Steps barely include slow real movement, so this measures noise rather than motion.
    """
    return float(np.sqrt(np.mean(np.diff(x[window]) ** 2)))


def lag_ms(raw: np.ndarray, filtered: np.ndarray, t: np.ndarray) -> float:
    """How many samples the filtered curve trails the raw one, in milliseconds."""
    moving = t >= MOVE_START
    raw, filtered = raw[moving], filtered[moving]
    errors = [np.mean((filtered[k:] - raw[: len(raw) - k]) ** 2) for k in range(16)]
    return int(np.argmin(errors)) * float(np.median(np.diff(t))) * 1000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=8.0)
    parser.add_argument("--joint", default="right_wrist", choices=LANDMARK_NAMES)
    parser.add_argument("--replay", help="use a saved recording instead of the camera")
    args = parser.parse_args()
    joint = LANDMARK_NAMES.index(args.joint)

    if args.replay:
        data = np.load(args.replay)
        t, joints = data["t"], data["joints"]
    else:
        t, joints = record(args.seconds)
        RECORDING.parent.mkdir(exist_ok=True)
        np.savez(RECORDING, t=t, joints=joints)
        print(f"Saved the raw recording to {RECORDING}")
    if len(t) < 30:
        raise SystemExit("Too few tracked frames; stand further back and try again.")

    raw_xyz = joints[:, joint, :3].astype(np.float64)
    curves = {"raw": raw_xyz[:, 0] * IMAGE_WIDTH}
    for min_cutoff, beta in SETTINGS:
        filt = OneEuroFilter(min_cutoff, beta)
        out = np.array([filt(ti, p) for ti, p in zip(t, raw_xyz)])
        curves[f"min_cutoff={min_cutoff}, beta={beta}"] = out[:, 0] * IMAGE_WIDTH

    still = stillest_window(t, curves["raw"])
    print(f"\n{args.joint}, x position in pixels ({len(t)} tracked frames)")
    print(f"jitter measured in the stillest second: {t[still.start]:.1f}-{t[still.stop - 1]:.1f} s")
    print(f"{'setting':32} {'jitter (RMS step, px)':>22} {'lag (ms)':>10}")
    for name, x in curves.items():
        lag = 0.0 if name == "raw" else lag_ms(curves["raw"], x, t)
        print(f"{name:32} {jitter_px(x, still):22.3f} {lag:10.0f}")

    fig, (top, bottom) = plt.subplots(2, 1, figsize=(10, 7))
    for ax, window in ((top, (t[0], t[-1])), (bottom, (MOVE_START, MOVE_START + 1.5))):
        for name, x in curves.items():
            style = {"color": "lightgray", "lw": 1.5} if name == "raw" else {"lw": 1.8}
            ax.plot(t, x, label=name, **style)
        ax.set_xlim(*window)
        ax.set_ylabel(f"{args.joint} x (pixels)")
        ax.grid(alpha=0.3)
    top.set_title("Raw vs One Euro filtered")
    bottom.set_title("Zoom on fast motion")
    bottom.set_xlabel("time (s)")
    top.legend(loc="upper left", fontsize=8)
    OUTPUT.parent.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUTPUT, dpi=110)
    print(f"\nPlot saved to {OUTPUT}")


if __name__ == "__main__":
    main()
