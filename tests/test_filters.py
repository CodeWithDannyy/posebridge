import numpy as np

from perception.filters import JointSmoother, OneEuroFilter

DT = 1 / 30


def run(filt: OneEuroFilter, signal: np.ndarray) -> np.ndarray:
    return np.array([filt(i * DT, s) for i, s in enumerate(signal)])


def test_constant_signal_stays_constant():
    out = run(OneEuroFilter(), np.full(100, 0.5))

    np.testing.assert_allclose(out, 0.5)


def test_reduces_jitter_at_rest():
    rng = np.random.default_rng(0)
    noisy = 0.5 + rng.normal(0, 0.01, 300)

    smoothed = run(OneEuroFilter(min_cutoff=1.0, beta=0.0), noisy)

    assert smoothed[30:].std() < 0.5 * noisy[30:].std()


def test_beta_reduces_lag_on_fast_motion():
    ramp = 10.0 * DT * np.arange(150)          # moves at 10 units per second

    lag_no_beta = abs(run(OneEuroFilter(1.0, beta=0.0), ramp)[-1] - ramp[-1])
    lag_beta = abs(run(OneEuroFilter(1.0, beta=1.0), ramp)[-1] - ramp[-1])

    assert lag_beta < 0.5 * lag_no_beta


def test_bad_timestamp_returns_previous_output():
    filt = OneEuroFilter()
    first = filt(1.0, 0.3)

    assert filt(1.0, 0.9) == first             # same timestamp: ignored
    assert filt(0.5, 0.9) == first             # older timestamp: ignored


def test_filters_a_whole_joint_array():
    filt = OneEuroFilter()
    joints = np.random.default_rng(1).random((33, 3))

    out = filt(0.0, joints)
    out2 = filt(DT, joints + 0.01)

    assert out.shape == (33, 3) and out2.shape == (33, 3)


def test_joint_smoother_filters_positions_but_keeps_visibility():
    smoother = JointSmoother()
    first = np.full((33, 4), 0.5, dtype=np.float32)
    moved = first.copy()
    moved[:, :3] += 0.1
    moved[:, 3] = 0.7

    smoother(0.0, first)
    out = smoother(DT, moved)

    assert out.shape == (33, 4)
    assert np.all(out[:, :3] < moved[:, :3])        # positions lag behind: smoothed
    np.testing.assert_allclose(out[:, 3], 0.7)       # visibility passed straight through


def test_joint_smoother_resets_when_tracking_is_lost():
    smoother = JointSmoother()
    left = np.full((33, 4), 0.2, dtype=np.float32)
    right = np.full((33, 4), 0.8, dtype=np.float32)

    smoother(0.0, left)
    assert smoother(DT, None) is None
    out = smoother(2 * DT, right)

    np.testing.assert_allclose(out, right)           # no gliding in from the old pose
