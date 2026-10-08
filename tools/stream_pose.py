#Perception process: webcam -> pose -> (smoothing) -> UDP packets to Unity.
#Keys in the camera window: s = toggle smoothing, q / Esc = quit.
import argparse
import time

import cv2

from perception.camera import open_camera
from perception.filters import JointSmoother
from perception.fps import FpsCounter
from perception.packet import encode_packet
from perception.pose import MediaPipePose
from perception.skeleton import draw_skeleton
from perception.udp import UdpSender


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream pose packets to Unity.")
    parser.add_argument("--no-smoothing", action="store_true", help="start with smoothing off")
    args = parser.parse_args()

    pose = MediaPipePose()
    smoother = JointSmoother()         # image landmarks (fractions of the image)
    world_smoother = JointSmoother()   # world landmarks (metres); same settings for now
    smoothing = not args.no_smoothing
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
            # Monotonic clock (seconds) for MediaPipe's tracker and for the filter.
            t = time.perf_counter() - start

            joints, world = pose.process_with_world(frame, int(t * 1000))
            if smoothing:
                joints = smoother(t, joints)
                world = world_smoother(t, world)

            sender.send(encode_packet(frame_index, t_capture_ms, joints, world))
            frame_index += 1

            # The preview shows exactly what is sent.
            if joints is not None:
                draw_skeleton(frame, joints)
            frame = cv2.flip(frame, 1)
            fps = fps_counter.tick()
            status = "ON" if smoothing else "OFF"
            cv2.putText(frame, f"{fps:.1f} FPS | smoothing {status} (s)", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("PoseBridge sender", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("s"):
                smoothing = not smoothing
                smoother.reset()   # start fresh, don't blend with an old pose
                world_smoother.reset()
    finally:
        sender.close()
        pose.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
