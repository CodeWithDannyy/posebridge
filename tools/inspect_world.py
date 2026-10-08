#Capture one pose and print MediaPipe's 3D world landmarks (metres), with sanity checks.
#Stand back so your whole body is in frame, facing the camera.
import time

import numpy as np

from perception.camera import open_camera
from perception.pose import MediaPipePose
from perception.skeleton import (
    L_ANKLE, L_ELBOW, L_HIP, L_KNEE, L_SHOULDER, L_WRIST, LANDMARK_NAMES, NOSE,
    R_ANKLE, R_ELBOW, R_HIP, R_KNEE, R_SHOULDER, R_WRIST,
)

FRAMES_TO_SETTLE = 60

SEGMENTS = {
    "shoulder width": (L_SHOULDER, R_SHOULDER),
    "hip width": (L_HIP, R_HIP),
    "left upper arm": (L_SHOULDER, L_ELBOW),
    "left forearm": (L_ELBOW, L_WRIST),
    "right upper arm": (R_SHOULDER, R_ELBOW),
    "right forearm": (R_ELBOW, R_WRIST),
    "left thigh": (L_HIP, L_KNEE),
    "left shin": (L_KNEE, L_ANKLE),
    "right thigh": (R_HIP, R_KNEE),
    "right shin": (R_KNEE, R_ANKLE),
}


def main() -> None:
    pose = MediaPipePose()
    cap = open_camera()
    start = time.perf_counter()
    frames = []
    try:
        for _ in range(FRAMES_TO_SETTLE):
            ok, frame = cap.read()
            if not ok:
                break
            _, w = pose.process_with_world(frame, int((time.perf_counter() - start) * 1000))
            if w is not None:
                frames.append(w)
    finally:
        pose.close()
        cap.release()

    if len(frames) < 10:
        print("Too few frames with a person. Stand back so your body is in frame and retry.")
        return

    # One frame is one noisy guess; the median over many frames is a stable estimate.
    stack = np.array(frames)              # shape (n_frames, 33, 4)
    world = np.median(stack, axis=0)
    print(f"median over {len(frames)} frames\n")

    print(f"{'idx':>3}  {'name':<17} {'x (m)':>7} {'y (m)':>7} {'z (m)':>7} {'vis':>5}")
    for i, (x, y, z, vis) in enumerate(world):
        print(f"{i:>3}  {LANDMARK_NAMES[i]:<17} {x:7.3f} {y:7.3f} {z:7.3f} {vis:5.2f}")

    hip_mid = (world[L_HIP, :3] + world[R_HIP, :3]) / 2
    print("\n--- sanity checks ---")
    print(f"hip midpoint (should be ~0, 0, 0): {np.round(hip_mid, 3)}")
    print(f"nose y = {world[NOSE, 1]:.3f} m  (negative = above the hips, so y points DOWN)")
    print(f"left shoulder x = {world[L_SHOULDER, 0]:.3f}, right shoulder x = {world[R_SHOULDER, 0]:.3f}")
    print("\nsegment lengths in cm, joint centre to joint centre (median, and 10th-90th percentile range):")
    for name, (a, b) in SEGMENTS.items():
        lengths = np.linalg.norm(stack[:, a, :3] - stack[:, b, :3], axis=1) * 100
        p10, p50, p90 = np.percentile(lengths, [10, 50, 90])
        low = min(world[a, 3], world[b, 3])
        flag = "" if low >= 0.5 else "   (low visibility, guessed)"
        print(f"  {name:<16} {p50:5.1f}   ({p10:5.1f} - {p90:5.1f}){flag}")


if __name__ == "__main__":
    main()
