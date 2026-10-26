import threading
import time


def afficher_distance(distance):
    """Affiche une mesure et indique si un objet est trop proche."""
    print("\n────────────────────────────────────────────")
    print(f"[DISTANCE] Distance mesurée : {distance:.1f} cm")

    if 0 < distance < 15:
        print("[DISTANCE] Alerte : Objet très proche ! (< 15 cm)")
    else:
        print("[DISTANCE] Zone dégagée.")

    print("────────────────────────────────────────────")


def surveiller_distance(stop_event=None, intervalle=1.0):
    """Surveille et affiche la distance jusqu'à la demande d'arrêt."""
    import lcd_outil

    stop_event = stop_event or threading.Event()
    stop_event.wait(2)
    print("[DISTANCE] Surveillance démarrée.")

    while not stop_event.is_set():
        afficher_distance(lcd_outil.get_distance())
        stop_event.wait(intervalle)


if __name__ == "__main__":
    try:
        surveiller_distance()
    except KeyboardInterrupt:
        print("\n[DISTANCE] Arrêt par l'utilisateur.")
