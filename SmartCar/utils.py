import serial
import time

# --- CONFIGURATION DU PORT SÉRIE ---
# Remplace par 'COM4' (Windows) ou '/dev/ttyACM2' (Linux/Mac) selon ton installation
PORT = 'COM4'
BAUD_RATE = 9600

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2) # Laisse le temps à l'Arduino de redémarrer
    print(f"Connexion série établie sur {PORT}")
except Exception as e:
    print(f"Erreur de connexion série : {e}")
    ser = None

# État des LED (pour le suivi interne si besoin)
etat_led = {
    "gauche": False,
    "droite": False,
}

def envoyer_commande(cmd):
    """Envoie une commande texte à l'Arduino via le port série."""
    if ser and ser.is_open:
        ser.write((cmd + "\n").encode("ascii"))

# --- FONCTIONS DE CONTRÔLE DES MOTEURS ---
def avancer():
    envoyer_commande("G_ON")
    envoyer_commande("D_ON")
    etat_led["gauche"] = True
    etat_led["droite"] = True

def reculer():
    envoyer_commande("G_REV")
    envoyer_commande("D_REV")
    etat_led["gauche"] = False
    etat_led["droite"] = False

def arret():
    envoyer_commande("G_OFF")
    envoyer_commande("D_OFF")
    etat_led["gauche"] = False
    etat_led["droite"] = False

def tourner_droite():
    envoyer_commande("G_ON")
    envoyer_commande("D_OFF")
    etat_led["gauche"] = True
    etat_led["droite"] = False

def tourner_gauche():
    envoyer_commande("G_OFF")
    envoyer_commande("D_ON")
    etat_led["gauche"] = False
    etat_led["droite"] = True

# --- FONCTION DE LECTURE DES CAPTEURS ULTRASONS ---
def get_distances():
    """Lit et retourne un tuple (distance_avant, distance_arriere) depuis l'Arduino."""
    derniere_ligne = None
    
    if ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                while ser.in_waiting > 0:
                    ligne = ser.readline().decode('utf-8').strip()
                    if ligne:
                        derniere_ligne = ligne
                
                if derniere_ligne and "," in derniere_ligne:
                    avant, arriere = derniere_ligne.split(",")
                    return float(avant), float(arriere)
        except ValueError:
            pass
            
    return 0.0, 0.0