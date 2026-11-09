from aliot.aliot_obj import AliotObj
import time
import lcd_outil

time.sleep(5)

# Création de l'objet à partir du fichier de configuration
capteur = AliotObj("capteur")

def allumer(data):
    print("Action reçue du cloud : Allumer les LED")
    capteur.update_doc({
        "/doc/led_droite": True,
        "/doc/led_gauche": True
    })

def eteindre(data):
    print("Action reçue du cloud : Éteindre les LED")
    capteur.update_doc({
        "/doc/led_droite": False,
        "/doc/led_gauche": False
    })

CRITICAL_DISTANCE = 15

def start():
    while True:
        try:
            # Lecture des distances depuis les capteurs
            avant, arriere = lcd_outil.get_distances()
            
            texte_lcd = f"Av:{avant:.0f}cm | Ar:{arriere:.0f}cm"

            # Vérification si un obstacle est à moins de 15 cm
            obstacle_avant = (0 < avant < CRITICAL_DISTANCE)
            obstacle_arriere = (0 < arriere < CRITICAL_DISTANCE)

            # Définition des états des LED pour le document
            etat_led_droite = True if obstacle_avant else False
            etat_led_gauche = True if obstacle_arriere else False

            # Envoi des mesures et de l'état des LED au serveur ALIVEcode
            capteur.update_doc({
                "/doc/distance_avant": avant,
                "/doc/distance_arriere": arriere,
                "/doc/lcd_texte": texte_lcd,
                "/doc/led_droite": etat_led_droite,
                "/doc/led_gauche": etat_led_gauche
            })

            # Affichage d'alertes dans la console de ton terminal
            if obstacle_avant:
                print("ALERTE: Obstacle proche à l'AVANT ! (< 15 cm)")
            if obstacle_arriere:
                print("ALERTE: Obstacle proche à l'ARRIÈRE ! (< 15 cm)")

            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erreur dans la boucle : {e}")
            time.sleep(1)

# Écoute des changements sur le document
def distance_changes(value):
    if value.get("/doc/distance_avant", 99) < CRITICAL_DISTANCE:
        print("Alerte distance avant critique détectée via le cloud.")

capteur.listen_doc(["/doc/distance_avant"], callback=distance_changes)

# Liaison des événements et du démarrage
capteur.on_start(callback=start)
capteur.on_action_recv(action_id="allumer_led", callback=allumer)
capteur.on_action_recv(action_id="eteindre_led", callback=eteindre)

# Connexion de l'objet au serveur ALIVEcode
capteur.run()