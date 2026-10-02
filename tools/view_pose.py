#Webcam with a skeleton drawn on you and the FPS on screen. Press q to quit.
import time

import cv2

from perception.camera import open_camera
from perception.fps import FpsCounter
from perception.pose import MediaPipePose
from perception.skeleton import draw_skeleton


def main() -> None:
    pose = MediaPipePose()
    cap = open_camera()
    fps_counter = FpsCounter(30)
    start = time.perf_counter()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            timestamp_ms = int((time.perf_counter() - start) * 1000)
            joints = pose.process(frame, timestamp_ms)

            # Draw on the raw frame (landmark coordinates match it), THEN mirror.
            if joints is not None:
                draw_skeleton(frame, joints)
            frame = cv2.flip(frame, 1)

            # Text goes on after the flip, otherwise it would read backwards.
            fps = fps_counter.tick()
            cv2.putText(frame, f"{fps:.1f} FPS", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("PoseBridge M0", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
            try:
                if cv2.getWindowProperty("PoseBridge M0", cv2.WND_PROP_AUTOSIZE) < 0:
                    break
            except cv2.error:
                break
    finally:
        pose.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
