# joystick.py
import threading
import serial
import time
import outils

SERIAL_PORT = "COM3"
BAUD_RATE = 9600


def executer_joystick(serial_port=SERIAL_PORT, baud_rate=BAUD_RATE, stop_event=None):
    """Lit le joystick et contrôle ses LED jusqu'à la demande d'arrêt."""
    stop_event = stop_event or threading.Event()
    last_button_state = 1
    control_enabled = False

    try:
        with serial.Serial(serial_port, baud_rate, timeout=0.1) as ser:
            time.sleep(2)
            last_led_x_state = False
            last_led_y_state = False

            while not stop_event.is_set():
                data = outils.get_position(ser)

                if data is not None:
                    button_state = data["BOUTON"]
                    x_value = data["X"]
                    y_value = data["Y"]

                    print(
                        f"\r[JOYSTICK] X: {x_value:4d} | Y: {y_value:4d}",
                        end="",
                        flush=True,
                    )

                    if button_state == 0 and last_button_state == 1:
                        control_enabled = not control_enabled

                        if not control_enabled:
                            outils.eteindre_les_deux_leds(ser)
                            last_led_x_state = False
                            last_led_y_state = False
                        stop_event.wait(0.2)

                    last_button_state = button_state

                    if control_enabled:
                        led_x_actuelle = x_value > 600
                        led_y_actuelle = x_value < 400

                        if led_x_actuelle != last_led_x_state:
                            outils.allumer_led_x(ser, led_x_actuelle)
                            last_led_x_state = led_x_actuelle

                        if led_y_actuelle != last_led_y_state:
                            outils.allumer_led_y(ser, led_y_actuelle)
                            last_led_y_state = led_y_actuelle

                stop_event.wait(0.01)

    except serial.SerialException as erreur:
        print(f"\n[JOYSTICK] Erreur série : {erreur}")


if __name__ == "__main__":
    try:
        executer_joystick()
    except KeyboardInterrupt:
        print()
