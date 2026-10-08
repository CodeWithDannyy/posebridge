"""Download MediaPipe's pose model into models/ (skips it if already there)."""
import urllib.request
from pathlib import Path

URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)
DESTINATION = Path(__file__).resolve().parent.parent / "models" / "pose_landmarker_lite.task"


def main() -> None:
    if DESTINATION.exists():
        print(f"Already there: {DESTINATION} ({DESTINATION.stat().st_size / 1e6:.1f} MB)")
        return
    DESTINATION.parent.mkdir(exist_ok=True)
    print(f"Downloading {URL}")
    urllib.request.urlretrieve(URL, DESTINATION)
    print(f"Saved to {DESTINATION} ({DESTINATION.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
