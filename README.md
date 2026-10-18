# Air Pen — Draw in the Air with Python

Draw glowing neon lines on a black canvas by moving your index finger in front of your laptop webcam. Show the canvas on a wall with a projector.

- **Language:** Python only (OpenCV + MediaPipe). No JavaScript, HTML or CSS.
- **Hand detection:** done by your **laptop webcam** and MediaPipe. The projector only **displays** the screen; it does not detect your hand.

## Project structure

```
air-pen/
├── main.py            # the application
├── config.py          # settings: camera, colors, brush, smoothing, glow
├── requirements.txt   # Python packages
└── README.md          # this file
```

## 1. Installation (Windows + VS Code)

Use the VS Code terminal: **Terminal → New Terminal** (PowerShell is fine).

### Step 1 — Check Python

```powershell
python --version
```

You need **Python 3.9 – 3.12** (3.11 or 3.12 recommended). MediaPipe does not provide packages for newer Python versions, so Python 3.13+ will fail at install time. If you have none, install 3.12 from python.org and tick **"Add python.exe to PATH"**.

To see all installed versions: `py -0`

### Step 2 — Create the project folder

```powershell
mkdir air-pen
cd air-pen
code .
```

`code .` reopens VS Code inside the folder. Open a new terminal again (Terminal → New Terminal).

### Step 3 — Create the four files

In VS Code, create `main.py`, `config.py`, `requirements.txt`, `README.md` in the `air-pen` folder and paste in the provided code.

### Step 4 — Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of the terminal line.

If PowerShell says *"running scripts is disabled"*:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

(Or use Command Prompt and run `.venv\Scripts\activate.bat`.)

If you have several Python versions, create the environment with a specific one, e.g. `py -3.12 -m venv .venv`.

If VS Code asks which interpreter to use, choose the one inside `.venv`.

### Step 5 — Install the packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6 — Run

```powershell
python main.py
```

Two windows open: **Air Pen - Canvas** (the drawing) and **Air Pen - Camera** (your camera, landmarks, help panel). Allow camera access if Windows asks.

## 2. Using the Air Pen

1. Sit about 40–80 cm from the webcam with good light on your hand.
2. Hold one hand up with the index finger pointing up. Move it to draw.
3. Move your hand out of view — the drawing stays until you clear it.

| Key | Action |
|---|---|
| `D` | Drawing on / off |
| `C` | Clear canvas |
| `E` | Eraser on / off |
| `1` `2` `3` `4` | Cyan / Magenta / Green / Yellow |
| `+` or `=` | Thicker brush |
| `-` | Thinner brush |
| `F` | Fullscreen / projection mode (canvas window) |
| `G` | Gestures on / off |
| `H` | Hide / show help panel |
| `Q` or `Esc` | Quit |

Keys work when either window is selected.

### Optional gestures (off by default)

Press `G` to turn them on:

- **Only index finger up** → draw
- **Index finger lowered / fist** → stop drawing
- **Open palm (all four fingers up)** → pause

Gestures assume your hand is upright facing the camera. If they feel unreliable, turn them off with `G` and use `D`.

## 3. Using a projector

1. Plug the projector in with HDMI (or USB-C / wireless display) and turn it on.
2. Press **Windows + P** and choose:
   - **Extend** (recommended): the projector is a second screen. You keep the camera window on your laptop.
   - **Duplicate**: the projector shows exactly what your laptop shows.
3. Start the Air Pen. Drag the **Air Pen - Canvas** window onto the projector screen (Extend mode).
4. Click that window and press **F** for fullscreen. Press **F** again to leave.
5. Point the projector at a wall (a dark room gives the brightest neon look).
6. Stand where the **laptop webcam** can see your hand. The webcam tracks you; the wall is just a display.

The drawing keeps its proportions (16:9) and gets black bars if the projector has a different shape.

## 4. Troubleshooting

**"Could not open camera"**
- Close Zoom, Teams, Skype, the Camera app or browser tabs using the camera.
- Windows Settings → Privacy & security → Camera → allow camera access and **"Let desktop apps access your camera"**.
- Change `CAMERA_INDEX` in `config.py` to `1` or `2` (external webcam).

**`ERROR: Could not find a version that satisfies the requirement mediapipe`**
- Your Python is too new (3.13+) or 32-bit. Install 64-bit Python 3.12, then delete `.venv` and recreate it with `py -3.12 -m venv .venv`.

**`module 'mediapipe' has no attribute 'solutions'`**
- Wrong MediaPipe version. Run: `pip install "mediapipe>=0.10.14,<0.10.22"`.

**NumPy errors (e.g. "numpy.core.multiarray failed to import")**
- Run: `pip install "numpy>=1.26,<2"`.

**Hand not detected / lines jumpy**
- Add light, use a plain background, keep the whole hand in view.
- Lines too shaky → lower `SMOOTHING` in `config.py` (e.g. `0.3`). Pen lags → raise it (e.g. `0.7`).

**Program is slow**
- Lower `CAMERA_WIDTH`/`CAMERA_HEIGHT`, or reduce `GLOW_SCALE` (e.g. `0.2`).

**Pen moves the wrong way**
- The camera view is already mirrored. If a particular camera behaves differently, tell me which one.

## 5. Possible future improvements

- Save the drawing as a PNG (key `S`).
- Undo the last stroke.
- On-screen color buttons you "tap" with your finger.
- Two-hand support and a more robust pinch gesture.
- Calibrating a projected area to the camera view.

## Note on testing

Written for Python 3.9–3.12 with the library versions listed in `requirements.txt`. Webcam and projector behaviour depends on your hardware and has not been confirmed on your machine.
