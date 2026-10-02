#Capture one pose and print the joints array, to see what the data looks like.
import time

from perception.camera import open_camera
from perception.pose import MediaPipePose
from perception.skeleton import L_HIP, L_KNEE, LANDMARK_NAMES

FRAMES_TO_SETTLE = 60  # give the tracker ~2 seconds to lock on, keep the last pose


def main() -> None:
    pose = MediaPipePose()
    cap = open_camera()
    start = time.perf_counter()
    joints = None
    try:
        for _ in range(FRAMES_TO_SETTLE):
            ok, frame = cap.read()
            if not ok:
                break
            result = pose.process(frame, int((time.perf_counter() - start) * 1000))
            if result is not None:
                joints = result
    finally:
        pose.close()
        cap.release()

    if joints is None:
        print("No person found. Stand back so your body is in frame and retry.")
        return

    print(f"shape: {joints.shape}   dtype: {joints.dtype}\n")
    print(f"{'idx':>3}  {'name':<17} {'x':>7} {'y':>7} {'z':>7} {'vis':>5}")
    for i, (x, y, z, vis) in enumerate(joints):
        print(f"{i:>3}  {LANDMARK_NAMES[i]:<17} {x:7.3f} {y:7.3f} {z:7.3f} {vis:5.2f}")

    print("\n--- indexing demos ---")
    print("joints[L_KNEE]       (one row):    ", joints[L_KNEE])
    print("joints[L_KNEE, 1]    (one number): ", joints[L_KNEE, 1])
    print("joints[:, 3].min()   (lowest visibility of all 33):", joints[:, 3].min())
    print("joints[L_KNEE] - joints[L_HIP]  (hip -> knee vector):",
          joints[L_KNEE] - joints[L_HIP])


if __name__ == "__main__":
    main()
