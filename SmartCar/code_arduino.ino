#include <LiquidCrystal.h>

// --- 1. CONFIGURATION LCD ---
// Pins: RS=6, E=10, D4=A2, D5=A3, D6=A4, D7=A5
LiquidCrystal lcd(6, 10, A2, A3, A4, A5);

// --- 2. CONFIGURATION MOTOR SHIELD REV3 ---
// Canal A (Moteur Gauche)
const int DIR_GAUCHE_PIN = 12;
const int PWM_GAUCHE_PIN = 3;
const int FREIN_GAUCHE_PIN = 9;

// Canal B (Moteur Droit - Inversé physiquement)
const int DIR_DROIT_PIN = 13;
const int PWM_DROIT_PIN = 11;
const int FREIN_DROIT_PIN = 8;

const int VITESSE = 255;

// --- 3. CAPTEURS ULTRASONS (Mode 1 broche Trig/Echo) ---
const int capteurAvant = 7;   // Pin 2 (libre)
const int capteurArriere = 4; // Pin 7 (libre)

// --- 4. BROCHES DES LED ---
const int LED_GAUCHE_PIN = 2;
const int LED_DROITE_PIN = 5;

// --- VARIABLES GLOBALES ---
String commande = "";
unsigned long tempsPrecedent = 0;
const long intervalleClignotement = 500; // 500 ms (0.5s)
bool etatLedBlink = LOW;
bool moteurGaucheMarche = false;
bool moteurDroitMarche = false;

// Fonction de contrôle des moteurs (avec inversion de la roue droite)
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

// Fonction de mesure pour les ultrasons (1 broche)
long mesurerDistance(int pinCapteur) {
  pinMode(pinCapteur, OUTPUT);
  digitalWrite(pinCapteur, LOW);
  delayMicroseconds(2);
  digitalWrite(pinCapteur, HIGH);
  delayMicroseconds(10);
  digitalWrite(pinCapteur, LOW);
  
  pinMode(pinCapteur, INPUT);
  long duration = pulseIn(pinCapteur, HIGH, 30000); // Timeout de 30ms
  if (duration == 0) return 0;
  return duration * 0.034 / 2;
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

  // Initialisation de l'écran LCD : 16 colonnes et 2 lignes
  lcd.begin(16, 2);

  // Sécurité au démarrage : tout couper
  commanderMoteur(true, 0);
  commanderMoteur(false, 0);
  digitalWrite(LED_GAUCHE_PIN, LOW);
  digitalWrite(LED_DROITE_PIN, LOW);
}

void loop() {
  // --- 1. LECTURE DES COMMANDES SÉRIE (VENANT DE PYTHON) ---
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

  // --- 2. MESURE DES CAPTEURS ULTRASONS ---
  long distanceAv = mesurerDistance(capteurAvant);
  long distanceAr = mesurerDistance(capteurArriere);

  // --- 3. AFFICHAGE SUR L'ÉCRAN LCD (16x2) ---
  lcd.setCursor(0, 0);
  lcd.print("Av:");
  lcd.print(distanceAv);
  lcd.print("cm    "); // Efface les résidus

  lcd.setCursor(0, 1);
  lcd.print("Ar:");
  lcd.print(distanceAr);
  lcd.print("cm    ");

  // --- 4. ENVOI DES DISTANCES VERS PYTHON ---
  // Format : "distanceAv,distanceAr" (ex: "25,120")
  Serial.print(distanceAv);
  Serial.print(",");
  Serial.println(distanceAr);

  // --- 5. GESTION DU CLIGNOTEMENT DES LED (SANS BLOQUER) ---
  unsigned long tempsActuel = millis();
  if (tempsActuel - tempsPrecedent >= intervalleClignotement) {
    tempsPrecedent = tempsActuel;
    etatLedBlink = !etatLedBlink;
  }

  // --- 6. APPLICATION DE LA LOGIQUE DES LED ---
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

  delay(50); // Petite pause pour stabiliser le tout
}