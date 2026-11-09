# Documentation: https://alivecode.ca/docs/aliot
import threading
from aliot.aliot_obj import AliotObj
from time import sleep
from utils import set_led, toggle_led, get_led_state

# Création de l'objet à partir du fichier de configuration
SmartCar = AliotObj("SmartCar")

def avancer(data):
    global direction
    direction = None
    SmartCar.update_doc({
        "/doc/avancer": True,
        "/doc/reculer": False,
        "/doc/droite": False,
        "/doc/gauche": False,
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

def reculer(data):
    global direction
    direction = None
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": True,
        "/doc/droite": False,
        "/doc/gauche": False,
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

def droite(data):
    global direction
    direction = "droite"
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": False,
        "/doc/droite": True,
        "/doc/gauche": False,
        "/doc/led_droite": True,
        "/doc/led_gauche": False
    })

def gauche(data):
    global direction
    direction = "gauche"
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": False,
        "/doc/droite": False,
        "/doc/gauche": True,
        "/doc/led_droite": False,
        "/doc/led_gauche": True
    })

def arret(data):
    global direction
    direction = None
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": False,
        "/doc/droite": False,
        "/doc/gauche": False,
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

def clignoter_leds():
    while True:
        led = direction

        if led in ("gauche", "droite"):
            autre_led = "droite" if led == "gauche" else "gauche"
            if get_led_state(autre_led):
                set_led(autre_led, False)

            toggle_led(led)
            sleep(0.5)  # intervalle du clignotement
        else:
            for nom in ("gauche", "droite"):
                if get_led_state(nom):
                    set_led(nom, False)
            sleep(0.1)
threading.Thread(target=clignoter_leds, daemon=True).start()

def start():
    pass

# Appel de la fonction start une fois que l'objet se connecte au serveur
SmartCar.on_start(callback=start)

SmartCar.on_action_recv(action_id="avancer", callback=avancer)
SmartCar.on_action_recv(action_id="reculer", callback=reculer)
SmartCar.on_action_recv(action_id="droite", callback=droite)
SmartCar.on_action_recv(action_id="gauche", callback=gauche)
SmartCar.on_action_recv(action_id="arret", callback=arret)

# Connection de l'objet au serveur ALIVEcode
SmartCar.run()
