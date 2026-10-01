"""Compare camera backends and pixel formats to find the best real frame rate."""
import time

import cv2

FRAMES_TO_TIME = 60
BACKENDS = {"DSHOW": cv2.CAP_DSHOW, "MSMF": cv2.CAP_MSMF}
FORMATS = {"default": None, "MJPG": "MJPG", "YUY2": "YUY2"}


def measure(index: int, backend: int, fourcc: str | None) -> str:
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        return "cannot open"

    # Order matters: format first, then size and FPS, because some drivers
    # only offer high frame rates for certain formats.
    if fourcc is not None:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    ok, frame = cap.read()
    if not ok:
        cap.release()
        return "opened but cannot read frames"

    start = time.perf_counter()
    for _ in range(FRAMES_TO_TIME):
        cap.read()
    elapsed = time.perf_counter() - start
    cap.release()

    height, width, _ = frame.shape
    return f"{width}x{height}, measured {FRAMES_TO_TIME / elapsed:.1f} fps"


if __name__ == "__main__":
    index = 0
    for backend_name, backend in BACKENDS.items():
        for format_name, fourcc in FORMATS.items():
            result = measure(index, backend, fourcc)
            print(f"{backend_name:6} {format_name:8} -> {result}")
