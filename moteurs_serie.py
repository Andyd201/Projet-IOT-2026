"""
moteurs_serie.py - Côté Raspberry Pi : envoie des ordres moteurs à l'Arduino par USB.
Gère aussi le bouton ON/OFF de l'auto (branché sur l'Arduino).

Dépendance :
    sudo apt install python3-serial

Trouver le port de l'Arduino :
    ls /dev/ttyACM* /dev/ttyUSB*      -> en général /dev/ttyACM0

Utilisation :
    from moteurs_serie import Moteurs

    with Moteurs("/dev/ttyACM0") as m:
        m.attendre_on()          # attend qu'on appuie sur le bouton
        m.avancer(0.6)
        m.stop()

Test rapide :
    python3 moteurs_serie.py
"""

import time
import serial

REPONSES = ("OK", "ERR", "OFF", "PONG")


def _pwm(v):
    """Convertit -1.0..1.0 en -255..255."""
    v = max(-1.0, min(1.0, float(v)))
    return int(round(v * 255))


class Moteurs:
    def __init__(self, port="/dev/ttyACM0", baud=115200, timeout=1.0, on_change=None):
        """
        on_change : fonction optionnelle appelée avec True/False
                    quand le bouton allume ou éteint l'auto.
        """
        self.on_change = on_change
        self.auto_on = False
        self.ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2)  # l'Arduino redémarre à l'ouverture du port
        self.ser.reset_input_buffer()
        if not self.ping():
            raise ConnectionError(f"L'Arduino ne répond pas sur {port}")
        self.demander_etat()

    # --- Lecture des messages de l'Arduino ---

    def _traiter_ligne(self, ligne):
        """Met à jour l'état si c'est un message ETAT. Retourne True si traité."""
        if ligne.startswith("ETAT"):
            nouveau = ligne.endswith("ON")
            if nouveau != self.auto_on:
                self.auto_on = nouveau
                if self.on_change:
                    self.on_change(nouveau)
            self.auto_on = nouveau
            return True
        return False

    def _lire_ligne(self):
        return self.ser.readline().decode(errors="ignore").strip()

    def _envoyer(self, cmd):
        """Envoie une commande et attend sa réponse (en gérant les messages ETAT au passage)."""
        self.ser.write((cmd + "\n").encode())
        fin = time.time() + 1.0
        while time.time() < fin:
            ligne = self._lire_ligne()
            if not ligne:
                continue
            if self._traiter_ligne(ligne):
                continue
            if ligne in REPONSES:
                if ligne == "OFF":
                    self.auto_on = False
                return ligne
        return ""

    def verifier(self):
        """Lit les messages en attente (appuis sur le bouton) sans bloquer.
        À appeler souvent dans ta boucle principale."""
        while self.ser.in_waiting:
            ligne = self._lire_ligne()
            if ligne:
                self._traiter_ligne(ligne)
        return self.auto_on

    def demander_etat(self):
        self.ser.write(b"E\n")
        fin = time.time() + 1.0
        while time.time() < fin:
            ligne = self._lire_ligne()
            if ligne and self._traiter_ligne(ligne):
                break
        return self.auto_on

    def attendre_on(self):
        """Bloque jusqu'à ce que l'auto soit allumée avec le bouton."""
        while not self.verifier():
            time.sleep(0.05)

    def ping(self):
        return self._envoyer("P") == "PONG"

    # --- Contrôle de base (vitesses de -1.0 à 1.0) ---
    # Retourne True si accepté, False si refusé (ex. auto éteinte).

    def moteur_a(self, v):
        return self._envoyer(f"A {_pwm(v)}") == "OK"

    def moteur_b(self, v):
        return self._envoyer(f"B {_pwm(v)}") == "OK"

    def set(self, a, b):
        return self._envoyer(f"M {_pwm(a)} {_pwm(b)}") == "OK"

    def stop(self):
        return self._envoyer("S") == "OK"

    def freiner(self):
        return self._envoyer("F") == "OK"

    # --- Raccourcis robot 2 roues (A = gauche, B = droite) ---
    # Avec un seul moteur branché, B est ignoré par l'Arduino : tourner_* fait juste avancer/reculer A.

    def avancer(self, v=1.0):
        return self.set(v, v)

    def reculer(self, v=1.0):
        return self.set(-v, -v)

    def tourner_gauche(self, v=1.0):
        return self.set(-v, v)

    def tourner_droite(self, v=1.0):
        return self.set(v, -v)

    def rampe(self, depart, cible, duree=1.0, etapes=20):
        for i in range(1, etapes + 1):
            v = depart + (cible - depart) * i / etapes
            if not self.set(v, v):
                return False  # auto éteinte en cours de route
            time.sleep(duree / etapes)
        return True

    def fermer(self):
        try:
            self.stop()
        finally:
            self.ser.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.fermer()


def executer_moteurs(port="/dev/ttyACM0", stop_event=None):
    """Exécute la séquence moteur de test jusqu'à la demande d'arrêt."""
    import threading

    stop_event = stop_event or threading.Event()

    def changement(on):
        print("\n[MOTEURS] Auto", "ALLUMÉE" if on else "ÉTEINTE")

    print(f"[MOTEURS] Connexion à l'Arduino sur {port}...")
    with Moteurs(port, on_change=changement) as m:
        while not stop_event.is_set():
            if not m.verifier():
                stop_event.wait(0.05)
                continue

            etapes = [
                ("Avant 100 %", lambda: m.avancer(1.0), 2),
                ("Pause", lambda: m.stop(), 1),
                ("Arrière 100 %", lambda: m.reculer(1.0), 2),
            ]
            for nom, action, duree in etapes:
                if stop_event.is_set() or not action():
                    break
                print(f"\n[MOTEURS] {nom}")
                fin = time.time() + duree
                while (
                    time.time() < fin
                    and not stop_event.is_set()
                    and m.verifier()
                ):
                    stop_event.wait(0.05)
                if not m.auto_on:
                    break
            m.stop()
            print("\n[MOTEURS] Séquence finie ou interrompue")


if __name__ == "__main__":
    import sys

    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
    try:
        executer_moteurs(port)
    except KeyboardInterrupt:
        print("\n[MOTEURS] Arrêt")
