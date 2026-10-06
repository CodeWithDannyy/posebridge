import numpy as np

from perception.packet import SCHEMA_VERSION, decode_packet, encode_packet


def make_joints() -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.random((33, 4)).astype(np.float32)


def test_round_trip_keeps_values():
    joints = make_joints()
    packet = decode_packet(encode_packet(7, 1234.5678, joints))

    assert packet["v"] == SCHEMA_VERSION
    assert packet["frame"] == 7
    assert packet["tracked"] is True
    assert len(packet["joints"]) == 33 * 4
    np.testing.assert_allclose(packet["joints"], joints.ravel(), atol=1e-4)


def test_no_person_sends_untracked_empty_packet():
    packet = decode_packet(encode_packet(8, 1234.0, None))

    assert packet["tracked"] is False
    assert packet["joints"] == []


def test_packet_is_small_enough_for_one_datagram():
    data = encode_packet(0, 1.0, make_joints())

    assert len(data) < 3000  # a UDP datagram can carry up to 65507 bytes
