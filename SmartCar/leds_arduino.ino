// Définition des broches des moteurs
const int MOTEUR_GAUCHE_PIN = 2;
const int MOTEUR_DROIT_PIN = 3;

// Définition des broches des LED (ajuste selon ton montage, ex: pins 4 et 5)
const int LED_GAUCHE_PIN = 4;
const int LED_DROITE_PIN = 5;

// Variable pour stocker les données lues sur le port série
String commande = "";

// Variables pour la gestion du clignotement sans bloquer le programme (millis)
unsigned long tempsPrecedent = 0;
const long intervalleClignotement = 500; // Intervalle de 500 ms (0.5s)
bool etatLedBlink = LOW;

void setup() {
  // Initialisation de la communication série
  Serial.begin(9600);

  // Configuration des broches des moteurs en sortie
  pinMode(MOTEUR_GAUCHE_PIN, OUTPUT);
  pinMode(MOTEUR_DROIT_PIN, OUTPUT);

  // Configuration des broches des LED en sortie
  pinMode(LED_GAUCHE_PIN, OUTPUT);
  pinMode(LED_DROITE_PIN, OUTPUT);

  // Sécurité : tout éteindre au démarrage
  digitalWrite(MOTEUR_GAUCHE_PIN, LOW);
  digitalWrite(MOTEUR_DROIT_PIN, LOW);
  digitalWrite(LED_GAUCHE_PIN, LOW);
  digitalWrite(LED_DROITE_PIN, LOW);
}

void loop() {
  // 1. Lecture des commandes reçues via le port série (Python)
  while (Serial.available() > 0) {
    char caractere = Serial.read();
    
    if (caractere == '\n') {
      commande.trim(); // Nettoie les espaces ou retours chariot

      if (commande == "G_ON") {
        digitalWrite(MOTEUR_GAUCHE_PIN, HIGH);
      } 
      else if (commande == "G_OFF") {
        digitalWrite(MOTEUR_GAUCHE_PIN, LOW);
      } 
      else if (commande == "D_ON") {
        digitalWrite(MOTEUR_DROIT_PIN, HIGH);
      } 
      else if (commande == "D_OFF") {
        digitalWrite(MOTEUR_DROIT_PIN, LOW);
      }

      commande = "";
    } else {
      commande += caractere;
    }
  }

  // 2. Gestion du rythme de clignotement (alternance toutes les 500ms)
  unsigned long tempsActuel = millis();
  if (tempsActuel - tempsPrecedent >= intervalleClignotement) {
    tempsPrecedent = tempsActuel;
    etatLedBlink = !etatLedBlink; // Inverse l'état (HIGH <-> LOW)
  }

  // 3. Lecture de l'état actuel des moteurs
  bool moteurGaucheMarche = (digitalRead(MOTEUR_GAUCHE_PIN) == HIGH);
  bool moteurDroitMarche = (digitalRead(MOTEUR_DROIT_PIN) == HIGH);

  // 4. Application de la logique des LED
  // LED gauche clignote SEULEMENT si le moteur gauche tourne et le droit est arrêté
  if (moteurGaucheMarche && !moteurDroitMarche) {
    digitalWrite(LED_GAUCHE_PIN, etatLedBlink);
  } else {
    digitalWrite(LED_GAUCHE_PIN, LOW);
  }

  // LED droite clignote SEULEMENT si le moteur droit tourne et le gauche est arrêté
  if (moteurDroitMarche && !moteurGaucheMarche) {
    digitalWrite(LED_DROITE_PIN, etatLedBlink);
  } else {
    digitalWrite(LED_DROITE_PIN, LOW);
  }
}