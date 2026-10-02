#Camera access for PoseBridge.#
import cv2


def open_camera(index: int = 0, width: int = 640, height: int = 480) -> cv2.VideoCapture:
    # MSMF measured ~30 fps on this laptop in any light; DSHOW managed 10-20
    # (see tools/webcam_check.py).
    cap = cv2.VideoCapture(index, cv2.CAP_MSMF)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {index}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap
