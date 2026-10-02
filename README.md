# PoseBridge

Real-time markerless motion capture into Unity, with movement-quality scoring.

> **Status: in progress, started 29 Sept 2026.** Nothing is runnable yet. This README is the plan, and boxes get ticked as each milestone lands.

## What it will do

A webcam watches a person. A pose-estimation model turns each frame into a skeleton of 33 body landmarks. The skeleton is streamed over UDP into Unity, where it drives a rigged 3D avatar in real time. A scoring module then judges one movement, the squat, by measuring knee angle at depth, knee valgus and rep tempo, and counts repetitions.

## Planned architecture

```
[ webcam ] -> PERCEPTION (Python) -> BRIDGE (UDP) -> PRESENTATION (Unity / C#)
              OpenCV, pose model,    localhost,       background socket thread,
              smoothing, analytics   JSON per frame   avatar rig, HUD
              (PyTorch)              + timestamp
```

Every packet carries a capture timestamp, which makes end-to-end latency measurable.

## Milestones

- [x] **M0**: Keypoints on screen (webcam feed with a skeleton drawn on it, FPS printed)
- [ ] **M1**: End-to-end: Unity cubes move when I move
- [ ] **M2**: Real humanoid avatar, with smoothing
- [ ] **M3**: Squat analyser: knee angle, valgus flag, rep counter, score on a HUD
- [ ] **M4**: Measured results (latency p50/p95, FPS, rep-count accuracy, knee-angle error on ~50 hand-labelled clips) and write-up

## Stack

Python 3.12, OpenCV, MediaPipe, PyTorch, NumPy, Unity 6, C#

## Limitations

To be filled in as the project develops.
