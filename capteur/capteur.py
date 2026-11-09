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
    # Variables pour mémoriser les dernières valeurs valides (filtre anti-zéro)
    derniere_avant = 0
    derniere_arriere = 0

    while True:
        try:
            # Lecture brute des distances
            avant_brut, arriere_brut = lcd_outil.get_distances()
            
            # Filtre anti-zéro
            if avant_brut > 0:
                avant = avant_brut
                derniere_avant = avant_brut
            else:
                avant = derniere_avant

            if arriere_brut > 0:
                arriere = arriere_brut
                derniere_arriere = arriere_brut
            else:
                arriere = derniere_arriere
            
            texte_lcd = f"Av:{avant:.0f}cm | Ar:{arriere:.0f}cm"

            # Envoi UNIQUEMENT des mesures et du texte au cloud.
            # Le cloud se chargera d'allumer/éteindre les LED via tes déclencheurs.
            capteur.update_doc({
                "/doc/distance_avant": avant,
                "/doc/distance_arriere": arriere,
                "/doc/lcd_texte": texte_lcd
            })

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