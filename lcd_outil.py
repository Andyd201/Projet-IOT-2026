import serial
import time

PORT = '/dev/ttyACM2'  # Garde ton port habituel
BAUD_RATE = 9600

try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"Erreur de connexion au port série : {e}")
    ser = None

def get_distances():
    """Lit et retourne un tuple (distance_avant, distance_arriere)."""
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