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



## 1. Using the Air Pen

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

## 2. Using a projector

1. Plug the projector in with HDMI (or USB-C / wireless display) and turn it on.
2. Press **Windows + P** and choose:
   - **Extend** (recommended): the projector is a second screen. You keep the camera window on your laptop.
   - **Duplicate**: the projector shows exactly what your laptop shows.
3. Start the Air Pen. Drag the **Air Pen - Canvas** window onto the projector screen (Extend mode).
4. Click that window and press **F** for fullscreen. Press **F** again to leave.
5. Point the projector at a wall (a dark room gives the brightest neon look).
6. Stand where the **laptop webcam** can see your hand. The webcam tracks you; the wall is just a display.

The drawing keeps its proportions (16:9) and gets black bars if the projector has a different shape.


## Note on testing

Written for Python 3.9–3.12 with the library versions listed in `requirements.txt`. Webcam and projector behaviour depends on your hardware and has not been confirmed on your machine.
