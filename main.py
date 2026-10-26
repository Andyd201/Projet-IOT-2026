import lcd_outil
import time

time.sleep(2)  # Laisse le temps à la connexion série de s'établir

print("📏 Surveillance de la distance démarrée...\n")

while True:
    try:
        # Récupérer la distance depuis lcd_outil
        distance = lcd_outil.get_distance()

        # Affichage formaté
        print("────────────────────────────────────────────")
        print(f"📍 Distance mesurée : {distance:.1f} cm")

        if 0 < distance < 15:
            print("⚠️ Alerte : Objet très proche ! (< 15 cm)")
        else:
            print("✅ Zone dégagée.")
        
        print("────────────────────────────────────────────\n")

        time.sleep(1)

    except KeyboardInterrupt:
        print("\n⛔ Arrêt par l'utilisateur.")
        break