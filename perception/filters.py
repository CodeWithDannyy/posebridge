"""One Euro filter: smooths a noisy signal with little lag when it moves fast.

Casiez, Roussel and Vogel, "1 Euro Filter", CHI 2012.

Idea: a low-pass filter blends each new sample with the previous output.
  - Slow signal -> low cutoff -> heavy smoothing (kills jitter).
  - Fast signal -> high cutoff -> light smoothing (little lag).
The cutoff therefore rises with the signal's speed:

    cutoff = min_cutoff + beta * |speed|
"""
import numpy as np


class OneEuroFilter:
    """Works on a float or on a NumPy array (every element is filtered independently).

    min_cutoff: smoothing at rest in Hz. Lower = smoother but laggier.
    beta:       how quickly the cutoff rises with speed. Higher = less lag when moving.
    d_cutoff:   smoothing of the speed estimate itself, in Hz.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.0, d_cutoff: float = 1.0) -> None:
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()

    def reset(self) -> None:
        self._t_prev: float | None = None
        self._x_prev = None
        self._dx_prev = None

    @staticmethod
    def _alpha(cutoff, dt: float):
        # Smoothing factor of a first-order low-pass filter: 0 = frozen, 1 = no smoothing.
        tau = 1.0 / (2.0 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, t: float, x):
        """Filter sample `x` taken at time `t` (seconds). Returns the smoothed value."""
        x = np.asarray(x, dtype=np.float64)
        if self._t_prev is None:                      # first sample: nothing to blend with
            self._t_prev, self._x_prev, self._dx_prev = t, x, np.zeros_like(x)
            return x

        dt = t - self._t_prev
        if dt <= 0:                                   # duplicate or out-of-order timestamp
            return self._x_prev

        dx = (x - self._x_prev) / dt                  # raw speed
        a_d = self._alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1.0 - a_d) * self._dx_prev

        cutoff = self.min_cutoff + self.beta * np.abs(dx_hat)
        a = self._alpha(cutoff, dt)
        x_hat = a * x + (1.0 - a) * self._x_prev

        self._t_prev, self._x_prev, self._dx_prev = t, x_hat, dx_hat
        return x_hat


class JointSmoother:
    """Smooths a pose array of shape (n_joints, 4): x, y, z are filtered, visibility is kept.

    Defaults come from Phase 3 Step 1 (docs/smoothing.png): 1 frame of lag, no extra jitter.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 4.0, d_cutoff: float = 1.0) -> None:
        self._filter = OneEuroFilter(min_cutoff, beta, d_cutoff)

    def __call__(self, t: float, joints: np.ndarray | None) -> np.ndarray | None:
        if joints is None:
            # Tracking lost: forget the old pose, so a person re-entering the frame
            # appears where they are instead of gliding in from where they left.
            self._filter.reset()
            return None
        smoothed = joints.copy()
        smoothed[:, :3] = self._filter(t, joints[:, :3])
        return smoothed

    def reset(self) -> None:
        self._filter.reset()
