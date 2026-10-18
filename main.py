"""
main.py - Air Pen: draw in the air with your index finger.

HOW IT WORKS (plain English)
----------------------------
* OpenCV (cv2) talks to the webcam and shows windows on screen.
* MediaPipe Hands looks at each camera picture and finds 21 "landmarks" on your
  hand. A landmark is just a named point, like "tip of the index finger".
  Landmark number 8 is the index fingertip.
* The canvas is a big black picture (a NumPy array of pixels). When your
  fingertip moves, we draw a short colored line on that picture between the
  old position and the new position. Old lines stay because we never erase the
  canvas unless you press C.
* The neon glow is made by blurring a copy of the canvas and adding the blur
  back on top of the sharp lines.

Two windows are shown:
  1. "Air Pen - Canvas"  -> the clean drawing. Put THIS one on the projector.
  2. "Air Pen - Camera"  -> your camera, hand landmarks and the help panel.

The webcam sees your hand. The projector only displays what the computer
shows. The projector does NOT detect your hand.
"""

import sys
import math

import cv2
import numpy as np

import config

try:
    import mediapipe as mp
    # The classic MediaPipe Hands API. Some very new releases removed it.
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
except (ImportError, AttributeError) as error:
    print("ERROR: Could not load MediaPipe Hands:", error)
    print("Fix: use Python 3.9-3.12 and run:  pip install -r requirements.txt")
    sys.exit(1)


# MediaPipe landmark numbers we use.
INDEX_TIP = 8
# (tip, pip-joint) pairs. A finger is "up" when its tip is higher on the
# screen than its middle joint. In images, smaller y means higher up.
INDEX_FINGER = (8, 6)
OTHER_FINGERS = [(12, 10), (16, 14), (20, 18)]   # middle, ring, pinky


# ----------------------------------------------------------------------------
# Camera
# ----------------------------------------------------------------------------
def open_camera():
    """Open the webcam. Returns the camera object or None if it fails."""
    # On Windows the DirectShow backend (CAP_DSHOW) opens faster and more reliably.
    if sys.platform.startswith("win"):
        cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(config.CAMERA_INDEX)

    if not cap.isOpened():
        cap.release()
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
    return cap


# ----------------------------------------------------------------------------
# Hand helpers
# ----------------------------------------------------------------------------
def finger_is_up(hand, finger):
    """True if the fingertip is above its middle joint (finger is extended)."""
    tip_id, joint_id = finger
    return hand.landmark[tip_id].y < hand.landmark[joint_id].y


def read_gesture(hand):
    """
    Look at the hand and return one word:
      "DRAW"  -> only the index finger is up
      "PALM"  -> index, middle, ring and pinky all up (open palm = pause)
      "STOP"  -> anything else (for example index finger lowered / fist)
    This assumes your hand is upright facing the camera.
    """
    index_up = finger_is_up(hand, INDEX_FINGER)
    others_up = sum(1 for f in OTHER_FINGERS if finger_is_up(hand, f))

    if index_up and others_up == 0:
        return "DRAW"
    if index_up and others_up == len(OTHER_FINGERS):
        return "PALM"
    return "STOP"


def smooth_point(old_smooth, new_point, factor):
    """
    Blend the new fingertip position with the previous smoothed position.
    This reduces shaking. factor 1.0 = no smoothing, small = very smooth.
    """
    if old_smooth is None:
        return new_point
    x = old_smooth[0] + factor * (new_point[0] - old_smooth[0])
    y = old_smooth[1] + factor * (new_point[1] - old_smooth[1])
    return (x, y)


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------
def lighten(color):
    """Mix a color 60% toward white. Used for the bright core of a neon line."""
    return tuple(int(c * 0.4 + 255 * 0.6) for c in color)


def draw_neon_segment(canvas, p0, p1, color, thickness):
    """Draw one piece of neon line: a colored tube with a bright white-ish core."""
    cv2.line(canvas, p0, p1, color, thickness, cv2.LINE_AA)
    core_thickness = max(1, thickness // 3)
    cv2.line(canvas, p0, p1, lighten(color), core_thickness, cv2.LINE_AA)


def erase_segment(canvas, p0, p1, thickness):
    """Erase by drawing a thick BLACK line on the canvas."""
    cv2.line(canvas, p0, p1, (0, 0, 0), thickness, cv2.LINE_AA)


def render_glow(canvas):
    """
    Make the neon glow:
    1. Shrink the canvas (makes the blur fast).
    2. Blur it.
    3. Enlarge it and add it on top of the sharp canvas.
    """
    height, width = canvas.shape[:2]
    small = cv2.resize(canvas, None, fx=config.GLOW_SCALE, fy=config.GLOW_SCALE,
                       interpolation=cv2.INTER_AREA)
    blurred = cv2.GaussianBlur(small, (0, 0), config.GLOW_SIGMA)
    glow = cv2.resize(blurred, (width, height), interpolation=cv2.INTER_LINEAR)
    return cv2.addWeighted(canvas, 1.0, glow, config.GLOW_STRENGTH, 0)


def fit_to_window(image, window_name):
    """
    Resize the image to fill the window WITHOUT stretching it. Extra space is
    filled with black bars. This keeps the drawing correct when the window is
    resized or in fullscreen on a projector with a different shape.
    """
    try:
        _, _, win_w, win_h = cv2.getWindowImageRect(window_name)
    except cv2.error:
        return image
    if win_w <= 0 or win_h <= 0:
        return image

    img_h, img_w = image.shape[:2]
    scale = min(win_w / img_w, win_h / img_h)
    new_w = max(1, int(img_w * scale))
    new_h = max(1, int(img_h * scale))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    output = np.zeros((win_h, win_w, 3), dtype=np.uint8)
    x_offset = (win_w - new_w) // 2
    y_offset = (win_h - new_h) // 2
    output[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    return output


def set_fullscreen(window_name, fullscreen):
    """Switch a window between fullscreen and normal."""
    mode = cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, mode)


# ----------------------------------------------------------------------------
# On-screen text
# ----------------------------------------------------------------------------
HELP_LINES = [
    "D  draw on/off",
    "C  clear canvas",
    "E  eraser",
    "1-4  cyan / magenta / green / yellow",
    "+ / -  brush size",
    "G  gestures on/off",
    "F  fullscreen (projector)",
    "H  hide/show help",
    "Q or Esc  quit",
]


def draw_help_panel(image, state, gesture):
    """Draw the status and controls on the camera preview (not on the canvas)."""
    color_name = config.COLORS[state["color_index"]][0]
    pen_mode = "ERASER" if state["eraser"] else "PEN (" + color_name + ")"
    lines = [
        "Drawing: " + ("ON" if state["drawing"] else "OFF"),
        "Mode: " + pen_mode + "   Size: " + str(state["thickness"]),
        "Gestures: " + ("ON" if state["gestures"] else "OFF") + "   Seen: " + gesture,
    ]
    if state["show_help"]:
        lines += [""] + HELP_LINES

    line_height = 22
    panel_h = 12 + line_height * len(lines)
    panel_w = 380

    # Semi-transparent dark rectangle behind the text so it is easy to read.
    overlay = image.copy()
    cv2.rectangle(overlay, (5, 5), (5 + panel_w, 5 + panel_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)

    y = 5 + 20
    for text in lines:
        cv2.putText(image, text, (14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 1, cv2.LINE_AA)
        y += line_height


# ----------------------------------------------------------------------------
# Keyboard
# ----------------------------------------------------------------------------
def handle_key(key, state, canvas):
    """Change the settings based on the key pressed. Returns False to quit."""
    if key == -1:
        return True

    key = key & 0xFF

    if key in (ord("q"), ord("Q"), 27):        # 27 = Esc
        return False

    elif key in (ord("d"), ord("D")):
        state["drawing"] = not state["drawing"]
    elif key in (ord("c"), ord("C")):
        canvas[:] = 0                          # Fill the whole canvas with black.
    elif key in (ord("e"), ord("E")):
        state["eraser"] = not state["eraser"]
    elif key in (ord("1"), ord("2"), ord("3"), ord("4")):
        state["color_index"] = key - ord("1")
        state["eraser"] = False                # Picking a color goes back to the pen.
    elif key in (ord("+"), ord("=")):
        state["thickness"] = min(config.MAX_THICKNESS,
                                 state["thickness"] + config.THICKNESS_STEP)
    elif key in (ord("-"), ord("_")):
        state["thickness"] = max(config.MIN_THICKNESS,
                                 state["thickness"] - config.THICKNESS_STEP)
    elif key in (ord("f"), ord("F")):
        state["fullscreen"] = not state["fullscreen"]
        set_fullscreen(config.CANVAS_WINDOW_NAME, state["fullscreen"])
    elif key in (ord("g"), ord("G")):
        state["gestures"] = not state["gestures"]
    elif key in (ord("h"), ord("H")):
        state["show_help"] = not state["show_help"]

    return True


# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------
def main():
    cap = open_camera()
    if cap is None:
        print("ERROR: Could not open camera number", config.CAMERA_INDEX)
        print("Things to try:")
        print("  - Close other apps using the camera (Zoom, Teams, Camera app).")
        print("  - Windows Settings > Privacy & security > Camera: allow desktop apps.")
        print("  - Change CAMERA_INDEX in config.py to 1 or 2.")
        sys.exit(1)

    # Create the hand tracker ONCE (not inside the loop).
    hands = mp_hands.Hands(
        static_image_mode=False,       # False = track between frames (faster).
        max_num_hands=1,               # We only need one hand.
        model_complexity=0,            # 0 = fastest model.
        min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
    )

    # The drawing canvas: black image, 3 color channels, 8-bit pixels.
    canvas = np.zeros((config.CANVAS_HEIGHT, config.CANVAS_WIDTH, 3), dtype=np.uint8)

    # All settings that can change while the program runs.
    state = {
        "drawing": True,
        "eraser": False,
        "color_index": config.DEFAULT_COLOR_INDEX,
        "thickness": config.DEFAULT_THICKNESS,
        "gestures": config.GESTURES_ENABLED_AT_START,
        "show_help": config.SHOW_HELP_AT_START,
        "fullscreen": False,
    }

    cv2.namedWindow(config.CANVAS_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.namedWindow(config.PREVIEW_WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config.CANVAS_WINDOW_NAME, 960, 540)

    smooth = None            # Smoothed fingertip position (x, y) on the canvas.
    previous = None          # Last point drawn. None means "start a new stroke".
    lost_frames = 0          # How many frames in a row the hand was missing.
    failed_reads = 0         # How many camera reads failed in a row.
    frame_count = 0

    print("Air Pen is running. Press Q or Esc in a window to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                failed_reads += 1
                if failed_reads > 30:
                    print("ERROR: The camera stopped sending pictures.")
                    break
                cv2.waitKey(10)
                continue
            failed_reads = 0

            # Mirror the picture so moving your hand right moves the pen right.
            frame = cv2.flip(frame, 1)
            frame_h, frame_w = frame.shape[:2]

            # MediaPipe wants RGB, OpenCV gives BGR.
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False          # Small speed-up.
            results = hands.process(rgb)

            gesture = "NONE"

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                lost_frames = 0

                # Landmark x and y are numbers from 0.0 to 1.0 across the picture.
                # Multiply by canvas size to get a canvas pixel position.
                tip = hand.landmark[INDEX_TIP]
                raw_point = (tip.x * config.CANVAS_WIDTH, tip.y * config.CANVAS_HEIGHT)
                smooth = smooth_point(smooth, raw_point, config.SMOOTHING)

                gesture = read_gesture(hand)

                # Decide if we should draw in this frame.
                should_draw = state["drawing"]
                if state["gestures"]:
                    should_draw = should_draw and gesture == "DRAW"

                point = (int(round(smooth[0])), int(round(smooth[1])))
                point = (min(max(point[0], 0), config.CANVAS_WIDTH - 1),
                         min(max(point[1], 0), config.CANVAS_HEIGHT - 1))

                if should_draw:
                    # If the finger jumped too far, start a new stroke.
                    if previous is not None:
                        jump = math.hypot(point[0] - previous[0], point[1] - previous[1])
                        if jump > config.MAX_JUMP_PIXELS:
                            previous = None

                    start = previous if previous is not None else point
                    if state["eraser"]:
                        erase_segment(canvas, start, point,
                                      state["thickness"] * config.ERASER_MULTIPLIER)
                    else:
                        color = config.COLORS[state["color_index"]][1]
                        draw_neon_segment(canvas, start, point, color, state["thickness"])
                    previous = point
                else:
                    previous = None              # Paused: the next draw starts fresh.

                # Show the landmarks and a ring on the camera preview.
                mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                cv2.circle(frame, (int(tip.x * frame_w), int(tip.y * frame_h)),
                           10, (0, 255, 255), 2)
            else:
                # No hand found.
                lost_frames += 1
                if lost_frames > config.LOST_FRAMES_TOLERANCE:
                    previous = None              # End the stroke: no stray lines.
                    smooth = None

            # ---------------- Canvas window (send this one to the projector) ----
            canvas_view = render_glow(canvas)
            if config.SHOW_CURSOR_ON_CANVAS and smooth is not None:
                cursor = (int(smooth[0]), int(smooth[1]))
                if state["eraser"]:
                    cursor_color = (255, 255, 255)
                    radius = (state["thickness"] * config.ERASER_MULTIPLIER) // 2
                else:
                    cursor_color = config.COLORS[state["color_index"]][1]
                    radius = max(6, state["thickness"] // 2 + 4)
                if not state["drawing"]:
                    cursor_color = (128, 128, 128)   # Gray ring = drawing is off.
                cv2.circle(canvas_view, cursor, radius, cursor_color, 1, cv2.LINE_AA)
            cv2.imshow(config.CANVAS_WINDOW_NAME,
                       fit_to_window(canvas_view, config.CANVAS_WINDOW_NAME))

            # ---------------- Camera preview window ----------------------------
            preview_h = int(frame_h * config.PREVIEW_WIDTH / frame_w)
            preview = cv2.resize(frame, (config.PREVIEW_WIDTH, preview_h))
            draw_help_panel(preview, state, gesture)
            cv2.imshow(config.PREVIEW_WINDOW_NAME, preview)

            # ---------------- Keyboard -----------------------------------------
            if not handle_key(cv2.waitKey(1), state, canvas):
                break

            # Quit if the user closed the canvas window with the X button.
            frame_count += 1
            if frame_count > 10:
                try:
                    if cv2.getWindowProperty(config.CANVAS_WINDOW_NAME,
                                             cv2.WND_PROP_VISIBLE) < 1:
                        break
                except cv2.error:
                    break

    finally:
        # Always release the camera and close windows, even after an error.
        cap.release()
        hands.close()
        cv2.destroyAllWindows()
        print("Air Pen closed.")


if __name__ == "__main__":
    main()
