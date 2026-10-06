"""Packet format shared by the Python sender and the Unity receiver.

One JSON object per camera frame, sent as one UDP datagram:

    v             schema version, so receiver and sender can detect a mismatch
    frame         frame counter; gaps in it reveal dropped packets
    t_capture_ms  Unix time in milliseconds when the frame was read from the camera
    tracked       False if no person was found in this frame
    joints        flat list [x0, y0, z0, vis0, x1, y1, z1, vis1, ...], 33 joints
                  (empty when tracked is False)
"""
import json

import numpy as np

SCHEMA_VERSION = 1


def encode_packet(frame: int, t_capture_ms: float, joints: np.ndarray | None) -> bytes:
    packet = {
        "v": SCHEMA_VERSION,
        "frame": frame,
        "t_capture_ms": round(t_capture_ms, 3),
        "tracked": joints is not None,
        # float32 -> float64 first, or JSON prints noise like 0.6520000100135803.
        "joints": [] if joints is None else joints.astype(np.float64).round(4).ravel().tolist(),
    }
    return json.dumps(packet, separators=(",", ":")).encode("utf-8")


def decode_packet(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))
