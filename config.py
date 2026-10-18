"""
config.py - Simple settings for the Air Pen.

Change the values here instead of digging through main.py.
Colors are in BGR order (Blue, Green, Red) because that is what OpenCV uses.
"""

# ----------------------------------------------------------------------------
# Camera
# ----------------------------------------------------------------------------
CAMERA_INDEX = 0          # 0 = built-in laptop webcam. Try 1 or 2 for other cameras.
CAMERA_WIDTH = 640        # Requested camera width. 640x480 is fast and good enough.
CAMERA_HEIGHT = 480       # Requested camera height.

# ----------------------------------------------------------------------------
# Drawing canvas (the black screen you draw on / project on the wall)
# ----------------------------------------------------------------------------
CANVAS_WIDTH = 1280       # Internal canvas size in pixels (16:9 shape).
CANVAS_HEIGHT = 720

# ----------------------------------------------------------------------------
# Pen colors (BGR). Keys 1-4 select these in order.
# ----------------------------------------------------------------------------
COLORS = [
    ("Cyan",    (255, 255, 0)),
    ("Magenta", (255, 0, 255)),
    ("Green",   (0, 255, 0)),
    ("Yellow",  (0, 255, 255)),
]
DEFAULT_COLOR_INDEX = 0   # 0 = first color in the list above (Cyan).

# ----------------------------------------------------------------------------
# Brush
# ----------------------------------------------------------------------------
DEFAULT_THICKNESS = 8     # Starting brush thickness in pixels.
MIN_THICKNESS = 2
MAX_THICKNESS = 40
THICKNESS_STEP = 2        # How much + and - change the thickness.
ERASER_MULTIPLIER = 3     # Eraser is this many times thicker than the pen.

# ----------------------------------------------------------------------------
# Smoothing and tracking
# ----------------------------------------------------------------------------
# SMOOTHING is a number between 0.05 and 1.0.
#   Lower  = smoother lines but the pen lags behind your finger.
#   Higher = faster pen but shakier lines. 1.0 = no smoothing.
SMOOTHING = 0.45

# If the finger "jumps" farther than this many canvas pixels in one frame we
# treat it as a tracking glitch and start a new stroke instead of a long line.
MAX_JUMP_PIXELS = 250

# Number of frames the hand may disappear before the stroke is ended.
# This hides tiny one-frame detection flickers.
LOST_FRAMES_TOLERANCE = 3

MIN_DETECTION_CONFIDENCE = 0.6
MIN_TRACKING_CONFIDENCE = 0.6

# ----------------------------------------------------------------------------
# Neon glow
# ----------------------------------------------------------------------------
GLOW_SCALE = 0.25         # Blur is done on a small copy (25%) to stay fast.
GLOW_SIGMA = 4            # Blur amount on the small copy. Bigger = wider glow.
GLOW_STRENGTH = 1.6       # How bright the glow is added back. 0 = no glow.

# ----------------------------------------------------------------------------
# Gestures (optional). Keyboard controls always work.
# Press G while running to switch gestures on or off.
# ----------------------------------------------------------------------------
GESTURES_ENABLED_AT_START = False

# ----------------------------------------------------------------------------
# Windows and display
# ----------------------------------------------------------------------------
CANVAS_WINDOW_NAME = "Air Pen - Canvas"      # Drag this window to the projector.
PREVIEW_WINDOW_NAME = "Air Pen - Camera"     # Camera view + help panel.
PREVIEW_WIDTH = 640
SHOW_CURSOR_ON_CANVAS = True                 # Small ring that shows where your fingertip is.
SHOW_HELP_AT_START = True
