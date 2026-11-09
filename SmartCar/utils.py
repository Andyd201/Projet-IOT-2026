import serial
import time
import threading
import math

# ser = serial.Serial('/dev/ttyACM2', 9600)
# ser = serial.Serial('COM3', 9600)

# C'est juste pour le test
class SerialSimule:
    def write(self, commande: bytes) -> int:
        print(f"[Arduino simulé] {commande.decode('ascii').strip()}")
        return len(commande)

etat_led = {
    "gauche": False,
    "droite": False,
}

def set_led(led, allumee):
    if led not in etat_led:
        raise ValueError("La LED doit être 'gauche' ou 'droite'")

    if led == "gauche":
        commande = "G_ON" if allumee else "G_OFF"
    else:
        commande = "D_ON" if allumee else "D_OFF"

    ser.write((commande + "\n").encode("ascii"))
    etat_led[led] = allumee

def toggle_led(led):
    if get_led_state(led):
        set_led(led, False)
    else:
        set_led(led, True)

def get_led_state(led):
    if led not in etat_led:
        raise ValueError("La LED doit être 'gauche' ou 'droite'")
    return etat_led[led]