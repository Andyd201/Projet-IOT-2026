import configparser
import os
import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

from aliot.aliot_obj import AliotObj

hand_controller = AliotObj("HandController")

# L'ID de la voiture est lu dans config.ini (section [SmartCar])
_config = configparser.ConfigParser()
_config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.ini"))
SMART_CAR_ID = _config["SmartCar"]["obj_id"]
FINGER_TIPS = [8, 12, 16, 20]
COMMAND_DELAY = 0.4

# Modèle de détection des mains (API MediaPipe Tasks, téléchargé au premier lancement)
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

# Liens entre les 21 points de la main, pour dessiner le squelette
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # pouce
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # majeur
    (9, 13), (13, 14), (14, 15), (15, 16),   # annulaire
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),  # auriculaire + paume
]


def get_model_path():
    """Télécharge le modèle de MediaPipe s'il n'est pas déjà présent."""
    if not os.path.exists(MODEL_PATH):
        print("Téléchargement du modèle MediaPipe (une seule fois)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def draw_hand(image, landmarks):
    """Dessine les points et les liens de la main sur l'image."""
    height, width = image.shape[:2]
    points = [(int(p.x * width), int(p.y * height)) for p in landmarks]
    for start, end in HAND_CONNECTIONS:
        cv2.line(image, points[start], points[end], (255, 255, 255), 2)
    for point in points:
        cv2.circle(image, point, 4, (0, 0, 255), -1)


def detect_fingers(landmarks, handedness):
    if handedness == "Right":
        thumb_open = landmarks[4].x < landmarks[3].x
    else:
        thumb_open = landmarks[4].x > landmarks[3].x

    fingers = [1 if thumb_open else 0]

    for tip_id in FINGER_TIPS:
        finger_open = landmarks[tip_id].y < landmarks[tip_id - 2].y
        fingers.append(1 if finger_open else 0)

    return fingers


def recognize_command(hands):
    if "Left" not in hands or "Right" not in hands:
        return None

    left = hands["Left"]
    right = hands["Right"]

    open_hand = [1, 1, 1, 1, 1]
    closed_hand = [0, 0, 0, 0, 0]
    index_only = [0, 1, 0, 0, 0]

    if left == open_hand and right == open_hand:
        return "arret"
    if left == closed_hand and right == closed_hand:
        return "avancer"
    if left == closed_hand and right == open_hand:
        return "droite"
    if left == open_hand and right == closed_hand:
        return "gauche"
    if left == index_only and right == index_only:
        return "reculer"

    return None


class PiCamera:
    """Caméra du Raspberry Pi (picamera2) avec la même interface que cv2.VideoCapture."""

    def __init__(self):
        from picamera2 import Picamera2

        self.picam = Picamera2()
        # "RGB888" donne des pixels dans l'ordre BGR, comme OpenCV
        config = self.picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        self.picam.configure(config)
        self.picam.start()

    def isOpened(self):
        return True

    def read(self):
        return True, self.picam.capture_array()

    def release(self):
        self.picam.stop()
        self.picam.close()


def open_camera():
    """Utilise la caméra du Pi si elle est disponible, sinon la webcam du PC."""
    try:
        cap = PiCamera()
        print("Caméra du Raspberry Pi utilisée.")
        return cap
    except Exception:
        print("Caméra du Pi indisponible, utilisation de la webcam.")
        return cv2.VideoCapture(0)


def start():
    cap = open_camera()
    # Sur Linux sans écran (SSH), on ne peut pas ouvrir de fenêtre
    show_window = os.name == "nt" or bool(os.environ.get("DISPLAY"))
    last_command = None
    pending_command = None
    pending_since = 0.0

    if not cap.isOpened():
        print("Impossible d'ouvrir la caméra.")
        hand_controller.stop()
        return

    if show_window:
        print("HandController connecté. Appuyez sur q pour quitter.")
    else:
        print("HandController connecté (sans fenêtre). Ctrl+C pour quitter.")

    options = vision.HandLandmarkerOptions(
        base_options=mp_tasks.BaseOptions(model_asset_path=get_model_path()),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    start_time = time.monotonic()
    last_timestamp = -1

    with vision.HandLandmarker.create_from_options(options) as hands_detector:
        while True:
            success, image = cap.read()
            if not success:
                print("Impossible de lire la caméra.")
                break

            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

            # Le mode VIDEO exige des timestamps (ms) strictement croissants
            timestamp = int((time.monotonic() - start_time) * 1000)
            timestamp = max(timestamp, last_timestamp + 1)
            last_timestamp = timestamp
            results = hands_detector.detect_for_video(mp_image, timestamp)

            detected_hands = {}

            for hand_landmarks, handedness_info in zip(
                results.hand_landmarks,
                results.handedness,
            ):
                handedness = handedness_info[0].category_name
                detected_hands[handedness] = detect_fingers(
                    hand_landmarks,
                    handedness,
                )
                draw_hand(image, hand_landmarks)

            command = recognize_command(detected_hands)
            now = time.monotonic()

            if command != pending_command:
                pending_command = command
                pending_since = now
            elif (
                command is not None
                and command != last_command
                and now - pending_since >= COMMAND_DELAY
            ):
                hand_controller.send_action(
                    target_id=SMART_CAR_ID,
                    action_id=command,
                )
                print(command)
                last_command = command

            if command is None:
                last_command = None

            display_command = command or "geste non reconnu"
            cv2.putText(
                image,
                display_command,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            if show_window:
                cv2.imshow("HandController", image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    cap.release()
    if show_window:
        cv2.destroyAllWindows()
    hand_controller.stop()


hand_controller.on_start(callback=start)
hand_controller.run()
