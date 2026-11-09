# Documentation: https://alivecode.ca/docs/aliot
from aliot.aliot_obj import AliotObj
import time
import lcd_outil

time.sleep(5)



capteur = AliotObj("capteur")

def allumer(data):
    capteur.LEDX_ON(True),
    capteur.LEDY_ON(True)
    capteur.update_component("Mylog", "LED allumée via le cloud.")
# Création de l'objet à partir du fichier de configuration

def eteindre(data):
    capteur.LEDX_ON(False),
    capteur.LEDY_ON(False)
    capteur.update_component("Mylog", "LED éteinte via le cloud.")

CRITICAL_DISTANCE = 15

def start():
    while True:
        try:
            # Lecture des distances depuis le capteur
            avant, arriere = lcd_outil.get_distances()
            
            texte_lcd = f"Av:{avant:.0f}cm | Ar:{arriere:.0f}cm"

            # Envoi des mesures au serveur ALIVEcode
            capteur.update_doc({
                "/doc/distance_avant": avant,
                "/doc/distance_arriere": arriere,
                "/doc/lcd_texte": texte_lcd
            })

            # Gestion des alertes d'obstacles
            if 0 < avant < CRITICAL_DISTANCE:
                capteur.update_component("Mylog", "ALERTE: Obstacle TROP PROCHE à l'AVANT ! (< 15 cm)")
            if 0 < arriere < CRITICAL_DISTANCE:
                capteur.update_component("Mylog", "ALERTE: Obstacle TROP PROCHE à l'ARRIÈRE ! (< 15 cm)")

            # Attente de 1 seconde avant la prochaine lecture
            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erreur de lecture des distances : {e}")
            time.sleep(1)

def distance_changes(value):
    if value.get("/doc/distance_avant", 99) < CRITICAL_DISTANCE:
        print("Alerte distance avant critique détectée via le cloud.")

# Écoute des changements sur le document
capteur.listen_doc(["/doc/distance_avant"], callback=distance_changes)

# Appel de la fonction start une fois que l'objet se connecte au serveur
capteur.on_start(callback=start)

capteur.on_action_recv(action_id="allumer_led", callback=allumer)
capteur.on_action_recv(action_id="eteindre_led", callback=eteindre)


# Connexion de l'objet au serveur ALIVEcode
capteur.run()