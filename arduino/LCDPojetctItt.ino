#include <LiquidCrystal.h>

// Déclaration des pins du LCD
LiquidCrystal lcd(11, 10, 5, 4, 3, 2);

// Capteur Avant (HC-SR04)
#define trigPinAv 6
#define echoPinAv 7

// Capteur Arrière (HC-SR04) - À adapter selon tes nouvelles pins libres
#define trigPinAr 8
#define echoPinAr 9

// Variables pour les distances
long durationAv, durationAr;
int distanceAv = 0;
int distanceAr = 0;

void setup() {
  // Configuration des broches pour l'avant
  pinMode(trigPinAv, OUTPUT);
  pinMode(echoPinAv, INPUT);

  // Configuration des broches pour l'arrière
  pinMode(trigPinAr, OUTPUT);
  pinMode(echoPinAr, INPUT);

  Serial.begin(9600);

  // Initialisation de l'écran LCD : 16 colonnes et 2 lignes
  lcd.begin(16, 2);
}

void loop() {
  // --- 1. MESURE CAPTEUR AVANT ---
  digitalWrite(trigPinAv, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPinAv, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPinAv, LOW);
  durationAv = pulseIn(echoPinAv, HIGH);
  distanceAv = durationAv * 0.034 / 2;

  // --- 2. MESURE CAPTEUR ARRIÈRE ---
  digitalWrite(trigPinAr, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPinAr, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPinAr, LOW);
  durationAr = pulseIn(echoPinAr, HIGH);
  distanceAr = durationAr * 0.034 / 2;

  // --- 3. AFFICHAGE SUR L'ÉCRAN LCD (16x2) ---
  // Ligne 0 (première ligne) : Affichage de l'avant
  lcd.setCursor(0, 0);
  lcd.print("Av:");
  lcd.print(distanceAv);
  lcd.print("cm     "); // Espaces pour effacer les anciens caractères résiduels

  // Ligne 1 (deuxième ligne) : Affichage de l'arrière
  lcd.setCursor(0, 1);
  lcd.print("Ar:");
  lcd.print(distanceAr);
  lcd.print("cm     ");

  // --- 4. ENVOI SÉRIE VERS PYTHON ---
  // On envoie les deux valeurs séparées par une virgule (ex: "15,30")
  Serial.print(distanceAv);
  Serial.print(",");
  Serial.println(distanceAr);

  delay(500); // Pause d'une demi-seconde avant la prochaine mesure
}