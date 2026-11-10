// Broches fixes de l'Arduino Motor Shield Rev3
const int DIR_GAUCHE_PIN = 12, PWM_GAUCHE_PIN = 3, FREIN_GAUCHE_PIN = 9;
const int DIR_DROIT_PIN = 13, PWM_DROIT_PIN = 11, FREIN_DROIT_PIN = 8;
const int VITESSE = 255;

// Définition des broches des LED (ajuste selon ton montage, ex: pins 4 et 5)
const int LED_GAUCHE_PIN = 4;
const int LED_DROITE_PIN = 5;

// Variable pour stocker les données lues sur le port série
String commande = "";

// Variables pour la gestion du clignotement sans bloquer le programme (millis)
unsigned long tempsPrecedent = 0;
const long intervalleClignotement = 500; // Intervalle de 500 ms (0.5s)
bool etatLedBlink = LOW;
bool moteurGaucheMarche = false;
bool moteurDroitMarche = false;

void commanderMoteur(bool gauche, int sens) {
  int dirPin = gauche ? DIR_GAUCHE_PIN : DIR_DROIT_PIN;
  int pwmPin = gauche ? PWM_GAUCHE_PIN : PWM_DROIT_PIN;
  int freinPin = gauche ? FREIN_GAUCHE_PIN : FREIN_DROIT_PIN;

  if (sens == 0) {
    analogWrite(pwmPin, 0);
    digitalWrite(freinPin, HIGH);
  } else {
    digitalWrite(freinPin, LOW);
    digitalWrite(dirPin, sens > 0 ? HIGH : LOW);
    analogWrite(pwmPin, VITESSE);
  }

  if (gauche) {
    moteurGaucheMarche = sens != 0;
  } else {
    moteurDroitMarche = sens != 0;
  }
}

void setup() {
  // Initialisation de la communication série
  Serial.begin(9600);

  pinMode(DIR_GAUCHE_PIN, OUTPUT);
  pinMode(PWM_GAUCHE_PIN, OUTPUT);
  pinMode(FREIN_GAUCHE_PIN, OUTPUT);
  pinMode(DIR_DROIT_PIN, OUTPUT);
  pinMode(PWM_DROIT_PIN, OUTPUT);
  pinMode(FREIN_DROIT_PIN, OUTPUT);

  // Configuration des broches des LED en sortie
  pinMode(LED_GAUCHE_PIN, OUTPUT);
  pinMode(LED_DROITE_PIN, OUTPUT);

  // Sécurité : tout éteindre au démarrage
  commanderMoteur(true, 0);
  commanderMoteur(false, 0);
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
        commanderMoteur(true, 1);
      } 
      else if (commande == "G_OFF") {
        commanderMoteur(true, 0);
      }
      else if (commande == "G_REV") {
        commanderMoteur(true, -1);
      } 
      else if (commande == "D_ON") {
        commanderMoteur(false, 1);
      } 
      else if (commande == "D_OFF") {
        commanderMoteur(false, 0);
      }
      else if (commande == "D_REV") {
        commanderMoteur(false, -1);
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

  // 3. Application de la logique des LED
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