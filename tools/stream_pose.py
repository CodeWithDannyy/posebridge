"""Perception process: webcam -> pose -> UDP packets to Unity. Press q to quit."""
import time

import cv2

from perception.camera import open_camera
from perception.fps import FpsCounter
from perception.packet import encode_packet
from perception.pose import MediaPipePose
from perception.skeleton import draw_skeleton
from perception.udp import UdpSender


def main() -> None:
    pose = MediaPipePose()
    sender = UdpSender()
    cap = open_camera()
    fps_counter = FpsCounter(30)
    start = time.perf_counter()
    frame_index = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            # Wall-clock stamp: a clock Unity can also read, so latency is measurable.
            t_capture_ms = time.time() * 1000

            # Monotonic clock for MediaPipe's tracker (needs ever-increasing times).
            joints = pose.process(frame, int((time.perf_counter() - start) * 1000))

            sender.send(encode_packet(frame_index, t_capture_ms, joints))
            frame_index += 1

            if joints is not None:
                draw_skeleton(frame, joints)
            frame = cv2.flip(frame, 1)
            fps = fps_counter.tick()
            cv2.putText(frame, f"{fps:.1f} FPS | frame {frame_index}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("PoseBridge sender", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        sender.close()
        pose.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
