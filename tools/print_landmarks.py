#Run MediaPipe pose on the webcam and print the nose landmark. Press q to quit.
import time

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision

from perception.camera import open_camera
from perception.fps import FpsCounter

MODEL_PATH = "models/pose_landmarker_lite.task"
NOSE = 0  # landmark index 0 in MediaPipe's 33-point skeleton


def main() -> None:
    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
    )
    landmarker = vision.PoseLandmarker.create_from_options(options)
    cap = open_camera()
    fps_counter = FpsCounter(30)
    start = time.perf_counter()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # OpenCV frames are BGR; MediaPipe expects RGB.
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((time.perf_counter() - start) * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            fps = fps_counter.tick()
            if result.pose_landmarks:
                nose = result.pose_landmarks[0][NOSE]
                print(
                    f"{fps:5.1f} fps | nose x={nose.x:.3f} y={nose.y:.3f} "
                    f"z={nose.z:.3f} visibility={nose.visibility:.2f}"
                )
            else:
                print(f"{fps:5.1f} fps | no person detected")

            # Mirror for display only; the model gets the un-mirrored frame.
            cv2.imshow("PoseBridge M0", cv2.flip(frame, 1))
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        landmarker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
