#Packet format shared by the Python sender and the Unity receiver.

#One JSON object per camera frame, sent as one UDP datagram:

#   v             schema version, so receiver and sender can detect a mismatch
#   frame         frame counter; gaps in it reveal dropped packets
#   t_capture_ms  Unix time in milliseconds when the frame was read from the camera
#   tracked       False if no person was found in this frame
#   joints        image landmarks, flat [x0, y0, z0, vis0, x1, ...], 33 joints;
#                 x, y are fractions of the image (empty when tracked is False)
#   world         world landmarks, same layout, x, y, z in METRES from the hip midpoint
#                 (empty when tracked is False or the model gives none)
#
# v2 (Phase 3): added "world".

import json

import numpy as np

SCHEMA_VERSION = 2


def _flat(array: np.ndarray | None) -> list[float]:
    # float32 -> float64 first, or JSON prints noise like 0.6520000100135803.
    return [] if array is None else array.astype(np.float64).round(4).ravel().tolist()


def encode_packet(
    frame: int,
    t_capture_ms: float,
    joints: np.ndarray | None,
    world: np.ndarray | None = None,
) -> bytes:
    packet = {
        "v": SCHEMA_VERSION,
        "frame": frame,
        "t_capture_ms": round(t_capture_ms, 3),
        "tracked": joints is not None,
        "joints": _flat(joints),
        "world": _flat(world) if joints is not None else [],
    }
    return json.dumps(packet, separators=(",", ":")).encode("utf-8")


def decode_packet(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))
