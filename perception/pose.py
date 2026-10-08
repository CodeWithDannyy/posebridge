#Pose estimation behind one small interface, so the model can be swapped.
from pathlib import Path
from typing import Protocol

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

# Resolve relative to this file, so scripts work from any working directory.
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "pose_landmarker_lite.task"


class PoseSource(Protocol):
    #Anything that turns a camera frame into joint positions.

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> np.ndarray | None:
        #Return an array of shape (n_joints, 4) = [x, y, z, visibility], or None.
        ...

    def close(self) -> None: ...


class MediaPipePose:
    #PoseSource backed by MediaPipe's PoseLandmarker (33 joints)

    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
        )
        self._landmarker = vision.PoseLandmarker.create_from_options(options)

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> np.ndarray | None:
        image, _ = self.process_with_world(frame_bgr, timestamp_ms)
        return image

    def process_with_world(
        self, frame_bgr: np.ndarray, timestamp_ms: int
    ) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Return (image, world), each (33, 4) = [x, y, z, visibility], or (None, None).

        image: x, y as fractions of the image (y down), z rough relative depth.
        world: x, y, z in METRES, origin at the midpoint of the hips,
               same axis directions as the image (x right, y down, z away from camera).
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)
        if not result.pose_landmarks:
            return None, None
        return _to_array(result.pose_landmarks[0]), _to_array(result.pose_world_landmarks[0])

    def close(self) -> None:
        self._landmarker.close()


def _to_array(landmarks) -> np.ndarray:
    return np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in landmarks], dtype=np.float32)
