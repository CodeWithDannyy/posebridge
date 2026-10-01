# PoseBridge Roadmap

> Real-time markerless motion capture into Unity, with movement-quality scoring.
> Webcam → pose model (Python) → UDP → rigged 3D avatar (Unity/C#) → squat analyser.

**Window:** 29 Sept – mid Oct 2026 (~2.5 weeks) · **Serves:** 51469, 54263, 54043, 54131

## How we work (every step)

1. **Concept:** what we're building and why, before any code.
2. **Code in small chunks:** each chunk explained line by line.
3. **You run it** and report what you see, whether it works or errors.
4. **Your turn:** a small tweak or exercise so you can check you've understood it.
5. **Commit** with a meaningful message, tick the box here, and add a line to `docs/LEARNING_LOG.md`.

## Environment notes (checked on this machine)

- Use **Python 3.12** for the venv, *not* 3.14 (the `py` default). MediaPipe has no 3.14 wheels.
- **Unity 6000.4.9f1** is installed. We use it instead of the spec's 2022 LTS, which is fine.
- **RTX 5070 Laptop (Blackwell):** PyTorch needs the **CUDA 12.8+ (cu128)** build. The default wheel won't use the GPU.
- git 2.54 and gh 2.93 are installed.

---

## PRE: Phase 0, Setup & Foundations (½–1 day)

- [ ] Create the `posebridge` venv on Python 3.12 and learn what a venv is and why we use one
- [ ] Folder layout: `perception/` (Python), `unity/` (Unity project), `tools/` (recording, labelling, eval), `data/` (git-ignored), `docs/`
- [ ] `git init`, add a `.gitignore` for both Python and Unity (Library/, Temp/, .venv, data/)
- [ ] Seed `README.md` with the pitch, the 3-box architecture, the milestone checkboxes and "Status: in progress, started 29 Sept 2026"
- [ ] Create the GitHub repo `posebridge`, **private** until the M1 GIF exists
- [ ] Webcam sanity check: confirm the camera index and its resolution and FPS
- [ ] Primer: images as NumPy arrays (H×W×3, BGR), what a pose model outputs (33 landmarks with x, y, z and visibility), normalised versus pixel coordinates

## Phase 1, M0: Keypoints on screen (1–2 days)

- [ ] OpenCV capture loop: read a frame, show it, quit on `q`
- [ ] FPS counter using a rolling average (learn why a single-frame FPS reading is noisy)
- [ ] Run MediaPipe **PoseLandmarker** (Tasks API) in VIDEO mode and download the `.task` model
- [ ] Draw the skeleton: joints as circles, bones as lines using a connection list
- [ ] Put a `PoseSource` interface around the model so we can swap in YOLO-Pose or a PyTorch model later
- [ ] **Done when:** the window shows you with a skeleton drawn on you and FPS printed

## Phase 2, M1: End-to-end, ugly ⭐ (the milestone that matters, 2–3 days)

- [ ] Design the packet schema: `{v, frame, t_capture_ms, joints: [[x,y,z,vis] × 33]}`
- [ ] Python UDP sender. Learn UDP vs TCP and why dropping a stale frame is fine here
- [ ] Python debug receiver, so we prove the sender works before Unity is involved
- [ ] Create the Unity project and learn the MonoBehaviour lifecycle (Awake, Start, Update)
- [ ] `UdpReceiver.cs`: a background thread reads the socket and a lock hands the latest packet to the main thread (Unity APIs are main-thread only)
- [ ] `JointCubes.cs`: spawn 33 cubes and move them from the packet
- [ ] **Fix coordinates here:** image Y-down → Unity Y-up, un-mirror the webcam, scale and centre
- [ ] Record a GIF, put it at the top of the README, and **make the repo public**
- [ ] **Done when:** the cubes move when you move

## Phase 3, M2: Real avatar and smoothing (3–4 days)

- [ ] Implement the **One-Euro filter** ourselves (about 30 lines) and understand its min_cutoff and beta parameters
- [ ] Plot raw vs smoothed for one joint to see the jitter disappear
- [ ] Switch to MediaPipe **world landmarks** (metres, hip-centred) to get a 3D-ish skeleton for the rig
- [ ] Get a Mixamo character, import it as **Humanoid** and check the Avatar mapping
- [ ] Primer: bone hierarchy, rest pose, local vs world rotation, quaternions and `FromToRotation`
- [ ] Retarget the limbs first (upper arm, forearm, thigh, shin), then hips, spine and head
- [ ] Handle low-visibility joints by holding the last good pose instead of snapping
- [ ] **Done when:** the avatar mirrors you smoothly with no visible jitter

## Phase 4, M3: Squat analytics (2–3 days)

- [ ] Design decision: analytics live in **Python** so the same code runs live and on recorded clips for validation. Unity only displays them
- [ ] Knee angle (hip–knee–ankle) using vectors and the dot product
- [ ] Rep counter: a state machine (STANDING → DOWN → BOTTOM → UP) with hysteresis thresholds
- [ ] Depth: the minimum knee angle per rep
- [ ] Valgus flag: knee x relative to the hip–ankle line, normalised by hip width
- [ ] Tempo: descent and ascent time per rep
- [ ] Combine the three into a single score
- [ ] **pytest** unit tests on synthetic angle sequences (first tests in the repo)
- [ ] Unity HUD: reps, depth, valgus warning and score using TextMeshPro
- [ ] Camera angle trade-off: depth is best measured from the side and valgus from the front. Pick about 45° and document why
- [ ] **Done when:** you squat, the rep counter ticks and the HUD scores you

## Phase 5: Make the PyTorch claim real (2–3 days)

Pick **one** (decided at the start of this phase):
- **(a)** Swap in YOLO-Pose and benchmark it against MediaPipe on accuracy and latency. This is the research line.
- **(b)** Train a small **TCN or LSTM** in PyTorch on keypoint sequences to classify the exercise (squat, lunge, jumping jack, idle). This is the stronger CV line. *Current lean: (b), because it teaches Dataset, DataLoader, nn.Module and the training loop.*

- [ ] Install PyTorch cu128 and confirm `torch.cuda.is_available()` returns True
- [ ] Data: record clips → extract keypoint sequences → windowing → train/val split by *session* (to avoid leakage)
- [ ] Model, training loop, validation, confusion matrix
- [ ] Wire it into the live pipeline so the HUD shows the detected exercise

## Phase 6, M4: Measure and write up (2–3 days)

- [ ] Latency: Python stamps `t_capture_ms` and Unity logs the time the frame is applied → CSV → **p50 and p95** with NumPy
- [ ] Throughput FPS and the **dropped-frame rate** from gaps in the frame index
- [ ] Recording tool: save about **50 squat clips** plus their keypoints
- [ ] Write the labelling protocol *before* labelling (what counts as a rep, and which frame is "the bottom")
- [ ] Hand labels: rep count per clip, plus the knee angle at the bottom measured with a small click-tool
- [ ] `eval.py` → rep-count accuracy % and knee-angle MAE (degrees) → a Markdown results table
- [ ] README final: GIF → what/why → stack → how to run (tested in a fresh venv) → results → limitations

---

## POST: Ship it

- [ ] Pin exact versions in `requirements.txt`, add an MIT LICENSE, and tag release `v1.0`
- [ ] Record a 30-second demo video and a GIF of you next to the avatar
- [ ] Fill in the **finished CV line** with real numbers (fps, ms latency, % rep accuracy)
- [ ] Website card: GIF, one sentence, the tags (Python, PyTorch, OpenCV, Unity, C#), and links to the repo and video
- [ ] Add Computer Vision and Deep Learning to Areas of Expertise (now earned)
- [ ] A 2-minute verbal walkthrough for supervisor calls, prepared from the learning log
- [ ] Limitations and future work: true 3D lifting, more movements, a prosthesis-emulator angle (54263)

## Known traps (from spec)

- Coordinate systems: fix them at M1 with the cubes, not at M2 with the rig.
- Jitter reads as broken: smoothing is not optional.
- Get 2D working end-to-end before any 3D lifting.
- Don't build a game or menus around it. The pipeline is the deliverable.
