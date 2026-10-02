#MediaPipe's 33-landmark body layout and a function to draw it.
import cv2

# Landmark indices we use (MediaPipe numbering). "Left" and "right" are the
# person's own left and right, not the image's.
NOSE = 0
L_SHOULDER, R_SHOULDER = 11, 12
L_ELBOW, R_ELBOW = 13, 14
L_WRIST, R_WRIST = 15, 16
L_HIP, R_HIP = 23, 24
L_KNEE, R_KNEE = 25, 26
L_ANKLE, R_ANKLE = 27, 28
L_HEEL, R_HEEL = 29, 30
L_FOOT, R_FOOT = 31, 32

# Names for all 33 landmarks, in MediaPipe's order (index = position in list).
LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer", "left_ear", "right_ear",
    "mouth_left", "mouth_right", "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow", "left_wrist", "right_wrist",
    "left_pinky", "right_pinky", "left_index", "right_index",
    "left_thumb", "right_thumb", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
    "left_heel", "right_heel", "left_foot_index", "right_foot_index",
]

# Each bone is a pair of landmark indices.
BONES = [
    (L_SHOULDER, R_SHOULDER),
    (L_SHOULDER, L_HIP), (R_SHOULDER, R_HIP), (L_HIP, R_HIP),
    (L_SHOULDER, L_ELBOW), (L_ELBOW, L_WRIST),
    (R_SHOULDER, R_ELBOW), (R_ELBOW, R_WRIST),
    (L_HIP, L_KNEE), (L_KNEE, L_ANKLE), (L_ANKLE, L_HEEL),
    (L_ANKLE, L_FOOT), (L_HEEL, L_FOOT),
    (R_HIP, R_KNEE), (R_KNEE, R_ANKLE), (R_ANKLE, R_HEEL),
    (R_ANKLE, R_FOOT), (R_HEEL, R_FOOT),
]

LEFT = {L_SHOULDER, L_ELBOW, L_WRIST, L_HIP, L_KNEE, L_ANKLE, L_HEEL, L_FOOT}
RIGHT = {R_SHOULDER, R_ELBOW, R_WRIST, R_HIP, R_KNEE, R_ANKLE, R_HEEL, R_FOOT}
JOINTS = {NOSE} | {i for bone in BONES for i in bone}

# Colours are BGR, not RGB.
COLOR_LEFT = (0, 165, 255)    # orange
COLOR_RIGHT = (255, 200, 0)   # light blue
COLOR_CENTER = (0, 255, 0)    # green


def _bone_color(a: int, b: int) -> tuple[int, int, int]:
    if a in LEFT and b in LEFT:
        return COLOR_LEFT
    if a in RIGHT and b in RIGHT:
        return COLOR_RIGHT
    return COLOR_CENTER


def draw_skeleton(frame, joints, min_visibility: float = 0.5) -> None:
    #Draw bones and joints onto `frame` in place.

    #`joints` is an array of shape (33, 4) = [x, y, z, visibility] per joint,
    #with x and y as fractions (0-1) of the image width and height.
    
    height, width = frame.shape[:2]  # shape is (rows, cols, ...) = (height, width)

    def point(i: int) -> tuple[int, int]:
        return int(joints[i, 0] * width), int(joints[i, 1] * height)

    def visible(i: int) -> bool:
        return joints[i, 3] >= min_visibility

    for a, b in BONES:
        if visible(a) and visible(b):
            cv2.line(frame, point(a), point(b), _bone_color(a, b), 3)
    for i in JOINTS:
        if visible(i):
            cv2.circle(frame, point(i), 5, (255, 255, 255), -1)  # -1 = filled
