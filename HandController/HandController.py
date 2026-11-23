import time

import cv2
import mediapipe as mp

from aliot.aliot_obj import AliotObj

hand_controller = AliotObj("HandController")

SMART_CAR_ID = "99d9b337-c504-4d22-9007-4d2cf6d5543f"
FINGER_TIPS = [8, 12, 16, 20]
COMMAND_DELAY = 0.4

mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


def detect_fingers(hand_landmarks, handedness):
    landmarks = hand_landmarks.landmark

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


def start():
    cap = cv2.VideoCapture(0)
    last_command = None
    pending_command = None
    pending_since = 0.0

    if not cap.isOpened():
        print("Impossible d'ouvrir la caméra.")
        hand_controller.stop()
        return

    print("HandController connecté. Appuyez sur q pour quitter.")

    with mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as hands_detector:
        while True:
            success, image = cap.read()
            if not success:
                print("Impossible de lire la caméra.")
                break

            image = cv2.flip(image, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rgb_image.flags.writeable = False
            results = hands_detector.process(rgb_image)
            rgb_image.flags.writeable = True

            detected_hands = {}

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness_info in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness,
                ):
                    handedness = handedness_info.classification[0].label
                    detected_hands[handedness] = detect_fingers(
                        hand_landmarks,
                        handedness,
                    )
                    mp_draw.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                    )

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
            cv2.imshow("HandController", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    hand_controller.stop()


hand_controller.on_start(callback=start)
hand_controller.run()
