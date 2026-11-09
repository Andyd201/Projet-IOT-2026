# Documentation: https://alivecode.ca/docs/aliot
from aliot.aliot_obj import AliotObj
from utils import (
    avancer as avancer_voiture,
    arret as arreter_voiture,
    reculer as reculer_voiture,
    tourner_droite as tourner_voiture_droite,
    tourner_gauche as tourner_voiture_gauche,
)

# Création de l'objet à partir du fichier de configuration
SmartCar = AliotObj("SmartCar")

def avancer(data):
    avancer_voiture()
    SmartCar.update_doc({
        "/doc/avancer": True,
        "/doc/reculer": False,
        "/doc/droite": False,
        "/doc/gauche": False,
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

def reculer(data):
    try:
        reculer_voiture()
    except NotImplementedError:
        SmartCar.update_doc({
            "/doc/avancer": False,
            "/doc/reculer": False,
            "/doc/droite": False,
            "/doc/gauche": False,
            "/doc/led_droite": False,
            "/doc/led_gauche": False
        })
        raise
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": True,
        "/doc/droite": False,
        "/doc/gauche": False,
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

def droite(data):
    tourner_voiture_droite()
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": False,
        "/doc/droite": True,
        "/doc/gauche": False,
        "/doc/led_droite": True,
        "/doc/led_gauche": False
    })

def gauche(data):
    tourner_voiture_gauche()
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": False,
        "/doc/droite": False,
        "/doc/gauche": True,
        "/doc/led_droite": False,
        "/doc/led_gauche": True
    })

def arret(data):
    arreter_voiture()
    SmartCar.update_doc({
        "/doc/avancer": False,
        "/doc/reculer": False,
        "/doc/droite": False,
        "/doc/gauche": False,
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

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
