#outil.py
import serial

def controler_led(ser_object, commande, description):
    try:
        ser_object.write(f"{commande}\n".encode('utf-8'))
        print(f"[ACTION] {description}")
    except serial.SerialException:
        print("[ERREUR] Impossible d'envoyer la commande")

def allumer_led_x(ser_object, allumer):
    if allumer:
        controler_led(ser_object, "LEDX_ON", "LED X -> ALLUMÉE")
    else:
        controler_led(ser_object, "LEDX_OFF", "LED X -> ÉTEINTE")

def allumer_led_y(ser_object, allumer):
    if allumer:
        controler_led(ser_object, "LEDY_ON", "LED Y -> ALLUMÉE")
    else:
        controler_led(ser_object, "LEDY_OFF", "LED Y -> ÉTEINTE")

def eteindre_les_deux_leds(ser_object):
    controler_led(ser_object, "LEDS_OFF", "Toutes les LEDS -> ÉTEINTES")

def get_position(ser_object):
    try:
        if ser_object.in_waiting > 0:
            line = ser_object.readline().decode('utf-8').strip()
            if "X:" in line and "Y:" in line:
                parts = line.split(',')
                button_state = 1
                x_value = 512
                y_value = 512
                for part in parts:
                    if part.startswith("BOUTON:"):
                        button_state = int(part.split(':')[1])
                    elif part.startswith("X:"):
                        x_value = int(part.split(':')[1])
                    elif part.startswith("Y:"):
                        y_value = int(part.split(':')[1])
                return {"BOUTON": button_state, "X": x_value, "Y": y_value}
    except (ValueError, IndexError, serial.SerialException) as e:
        print(f"[ERREUR LECTURE] {e}")
    return None
