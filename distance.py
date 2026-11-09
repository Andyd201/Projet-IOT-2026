import threading
import time
import lcd_outil

def afficher_distances(avant, arriere):
    """Affiche les mesures de l'avant et de l'arrière et gère les alertes."""
    print(f"\n========================================")
    print(f"[DISTANCE] Avant  : {avant:.1f} cm")
    print(f"[DISTANCE] Arrière : {arriere:.1f} cm")

    if 0 < avant < 15:
        print("[ALERTE] Obstacle TROP PROCHE à l'AVANT ! (< 15 cm)")
    if 0 < arriere < 15:
        print("[ALERTE] Obstacle TROP PROCHE à l'ARRIÈRE ! (< 15 cm)")
        
    print(f"========================================")

def surveiller_distance(stop_event=None, intervalle=1.0):
    """Surveille et affiche les distances en continu jusqu'à l'arrêt."""
    stop_event = stop_event or threading.Event()
    stop_event.wait(2)
    print("[DISTANCE] Surveillance démarrée.")

    while not stop_event.is_set():
        avant, arriere = lcd_outil.get_distances()
        afficher_distances(avant, arriere)
        stop_event.wait(intervalle)

if __name__ == "__main__":
    try:
        surveiller_distance()
    except KeyboardInterrupt:
        print("\n[DISTANCE] Arrêt par l'utilisateur.")