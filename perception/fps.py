#Rolling frame-rate measurement.
import time



class FpsCounter:
    #Average FPS over the last `window` frames.

    def __init__(self, window: int = 30) -> None:
        self._times = []
        self.window = window

    def tick(self) -> float:
        #Call once per frame. Returns the current FPS estimate.
        
        self._times.append(time.perf_counter())
        #print(len(self._times))
        if (len(self._times) > self.window):
            self._times.pop(0)

        if len(self._times) < 2:
            return 0.0

        elapsed = self._times[-1] - self._times[0]

        fps = (len(self._times) - 1)/elapsed

        return fps
