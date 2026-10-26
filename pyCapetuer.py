import RPi.GPIO as GPIO
from time import sleep
from lcd import LCD

# Configuration des broches du HC-SR04 (en numérotation BCM)
TRIG = 23
ECHO = 24

# Configuration des GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Initialisation de l'écran LCD
lcd = LCD()

def get_distance():
    """Fonction pour mesurer la distance avec le HC-SR04"""
    # Envoi d'une impulsion de 10 µs sur Trig
    GPIO.output(TRIG, False)
    sleep(0.00002)
    GPIO.output(TRIG, True)
    sleep(0.00001)
    GPIO.output(TRIG, False)
    
    # Attente du début de l'impulsion Echo
    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        
    # Attente de la fin de l'impulsion Echo
    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        
    # Calcul de la durée et conversion en centimètres (vitesse du son ~34300 cm/s)
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 1)

try:
    lcd.text("Mesure en cours", 0)
    sleep(1)
    
    while True:
        dist = get_distance()
        
        # Affichage sur l'écran LCD (selon ton modèle)
        lcd.text("Distance :      ", 0) # Ligne 0 avec des espaces pour effacer les résidus
        lcd.text(f"{dist} cm       ", 1) # Ligne 1 avec la valeur mesurée
        
        # Pause d'une demi-seconde avant la prochaine mesure
        sleep(0.5)

except KeyboardInterrupt:
    # Nettoyage propre lors d'un Ctrl+C
    lcd.clear()
    GPIO.cleanup()
    print("\nProgramme arrêté et GPIO nettoyés.")