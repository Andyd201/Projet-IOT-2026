# import serial
# import time

# # Remplace 'COM3' par ton port réel
# PORT = 'COM3'
# BAUD_RATE = 9600

# try:
#     # Initialisation de la liaison série
#     ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
#     time.sleep(2)  # Laisse le temps à la connexion de s'établir
# except Exception as e:
#     print(f"Erreur de connexion au port série : {e}")
#     ser = None

# def get_distance():
#     """Lit la distance envoyée par l'Arduino via le port série."""
#     if ser and ser.is_open:
#         try:
#             if ser.in_waiting > 0:
#                 ligne = ser.readline().decode('utf-8').strip()
#                 if ligne:
#                     return float(ligne)
#         except ValueError:
#             pass
#     return 0.0

import serial
import time

# Remplace 'COM3' par ton port réel
PORT = 'COM3'
BAUD_RATE = 9600

try:
    # Initialisation de la liaison série
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Laisse le temps à la connexion de s'établir
except Exception as e:
    print(f"Erreur de connexion au port série : {e}")
    ser = None

def get_distance():
    """Lit uniquement la toute dernière distance reçue, en éliminant le retard accumulé."""
    derniere_ligne = None
    
    if ser and ser.is_open:
        try:
            # S'il y a des données en attente dans le port série
            if ser.in_waiting > 0:
                # On lit TOUTES les lignes en attente dans la boucle pour 
                # ne garder que la toute dernière (la plus fraîche en temps réel)
                while ser.in_waiting > 0:
                    ligne = ser.readline().decode('utf-8').strip()
                    if ligne:
                        derniere_ligne = ligne
                
                if derniere_ligne:
                    return float(derniere_ligne)
        except ValueError:
            pass
            
    return 0.0