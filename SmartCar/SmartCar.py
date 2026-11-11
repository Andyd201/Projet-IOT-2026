# Documentation: https://alivecode.ca/docs/aliot
from aliot.aliot_obj import AliotObj
import time
from utils import (
    avancer as avancer_voiture,
    arret as arreter_voiture,
    reculer as reculer_voiture,
    tourner_droite as tourner_voiture_droite,
    tourner_gauche as tourner_voiture_gauche,
    get_distances
)

# Création de l'objet à partir du fichier de configuration
SmartCar = AliotObj("SmartCar")

CRITICAL_DISTANCE = 0  # Distance de sécurité en cm

# --- ACTIONS REÇUES DU CLOUD ---
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
    reculer_voiture()
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

# --- BOUCLE PRINCIPALE (CAPTEURS & CLOUD) ---
def start():
    derniere_avant = 0
    derniere_arriere = 0

    print("SmartCar connectée au cloud et prête !")
    
    while True:
        try:
            # 1. Lecture des distances via le port série
            avant_brut, arriere_brut = get_distances()
            
            # Filtre anti-zéro (garde la dernière valeur valide si le capteur renvoie 0)
            avant = avant_brut if avant_brut > 0 else derniere_avant
            if avant_brut > 0: derniere_avant = avant_brut

            arriere = arriere_brut if arriere_brut > 0 else derniere_arriere
            if arriere_brut > 0: derniere_arriere = arriere_brut
            
            texte_lcd = f"Av:{avant:.0f}cm | Ar:{arriere:.0f}cm"

            # 2. Sécurité anti-collision automatique à l'avant
            if avant < CRITICAL_DISTANCE and avant > 0:
                print(" Obstacle détecté à l'avant ! Arrêt d'urgence.")
                arreter_voiture()
                SmartCar.update_doc({
                    "/doc/avancer": False,
                    "/doc/reculer": False,
                    "/doc/droite": False,
                    "/doc/gauche": False,
                    "/doc/led_droite": False,
                    "/doc/led_gauche": False
                })

            # 3. Envoi des mesures au Cloud Aliot
            SmartCar.update_doc({
                "/doc/distance_avant": avant,
                "/doc/distance_arriere": arriere,
                "/doc/lcd_texte": texte_lcd
            })

            time.sleep(0.5)
            
        except KeyboardInterrupt:
            arreter_voiture()
            break
        except Exception as e:
            print(f"Erreur dans la boucle principale : {e}")
            time.sleep(1)

# --- LIAISON DES ÉVÉNEMENTS ---
SmartCar.on_start(callback=start)

SmartCar.on_action_recv(action_id="avancer", callback=avancer)
SmartCar.on_action_recv(action_id="reculer", callback=reculer)
SmartCar.on_action_recv(action_id="droite", callback=droite)
SmartCar.on_action_recv(action_id="gauche", callback=gauche)
SmartCar.on_action_recv(action_id="arret", callback=arret)
SmartCar.on_action_recv(action_id="allumer_led", callback=allumer_led)
SmartCar.on_action_recv(action_id="eteindre_led", callback=eteindre_led)

# Connexion de l'objet au serveur ALIVEcode
SmartCar.run()