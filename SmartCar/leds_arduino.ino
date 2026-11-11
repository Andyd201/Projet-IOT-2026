// --- BROCHES DU MOTOR SHIELD REV3 ---
// Canal A (Moteur Gauche)
const int DIR_GAUCHE_PIN = 12;
const int PWM_GAUCHE_PIN = 3;
const int FREIN_GAUCHE_PIN = 9;

// Canal B (Moteur Droit)
const int DIR_DROIT_PIN = 13;
const int PWM_DROIT_PIN = 11;
const int FREIN_DROIT_PIN = 8;

const int VITESSE = 255;

// --- BROCHES DES LED ---
const int LED_GAUCHE_PIN = 2;
const int LED_DROITE_PIN = 5;

// --- VARIABLES ---
String commande = "";
unsigned long tempsPrecedent = 0;
const long intervalleClignotement = 500; // 500 ms (0.5s)
bool etatLedBlink = LOW;
bool moteurGaucheMarche = false;
bool moteurDroitMarche = false;

// Fonction de contrôle des moteurs
void commanderMoteur(bool gauche, int sens) {
  int dirPin = gauche ? DIR_GAUCHE_PIN : DIR_DROIT_PIN;
  int pwmPin = gauche ? PWM_GAUCHE_PIN : PWM_DROIT_PIN;
  int freinPin = gauche ? FREIN_GAUCHE_PIN : FREIN_DROIT_PIN;

  if (sens == 0) {
    analogWrite(pwmPin, 0);
    digitalWrite(freinPin, HIGH);
  } else {
    digitalWrite(freinPin, LOW);
    
    if (gauche) {
      // Moteur gauche normal
      digitalWrite(dirPin, sens > 0 ? HIGH : LOW);
    } else {
      // Moteur droit INVERSÉ (on inverse HIGH et LOW)
      digitalWrite(dirPin, sens > 0 ? LOW : HIGH);
    }
    
    analogWrite(pwmPin, VITESSE);
  }

  if (gauche) {
    moteurGaucheMarche = sens != 0;
  } else {
    moteurDroitMarche = sens != 0;
  }
}

void setup() {
  Serial.begin(9600);

  // Initialisation des broches moteurs
  pinMode(DIR_GAUCHE_PIN, OUTPUT);
  pinMode(PWM_GAUCHE_PIN, OUTPUT);
  pinMode(FREIN_GAUCHE_PIN, OUTPUT);
  pinMode(DIR_DROIT_PIN, OUTPUT);
  pinMode(PWM_DROIT_PIN, OUTPUT);
  pinMode(FREIN_DROIT_PIN, OUTPUT);

  // Initialisation des broches LED
  pinMode(LED_GAUCHE_PIN, OUTPUT);
  pinMode(LED_DROITE_PIN, OUTPUT);

  // Sécurité au démarrage : tout éteindre
  commanderMoteur(true, 0);
  commanderMoteur(false, 0);
  digitalWrite(LED_GAUCHE_PIN, LOW);
  digitalWrite(LED_DROITE_PIN, LOW);
}

void loop() {
  // 1. Lecture des commandes reçues via le port série
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

  // 2. Gestion du clignotement des LED (sans bloquer le programme)
  unsigned long tempsActuel = millis();
  if (tempsActuel - tempsPrecedent >= intervalleClignotement) {
    tempsPrecedent = tempsActuel;
    etatLedBlink = !etatLedBlink;
  }

  // 3. Application de la logique des LED
  if (moteurGaucheMarche && !moteurDroitMarche) {
    digitalWrite(LED_GAUCHE_PIN, etatLedBlink);
  } else {
    digitalWrite(LED_GAUCHE_PIN, LOW);
  }

  if (moteurDroitMarche && !moteurGaucheMarche) {
    digitalWrite(LED_DROITE_PIN, etatLedBlink);
  } else {
    digitalWrite(LED_DROITE_PIN, LOW);
  }
}