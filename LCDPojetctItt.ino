// Importation de la bibliothèque 'LiquidCrystal'
#include <LiquidCrystal.h>

// Déclaration des pins du LCD (12, 11, 5, 4, 3, 2)
LiquidCrystal lcd(11, 10, 5, 4, 3, 2);

// Déclaration des pins du capteur HC-SR04 
// (On évite les pins 2 et 3 qui sont déjà occupés par l'écran LCD ci-dessus)
#define trigPin 7
#define echoPin 6

// Variables pour le calcul de la distance
long duration;
int distanceCm = 0;

void setup() {
  // Initialisation des broches du capteur de distance
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);

  // Initialisation de l'écran LCD : 16 colonnes et 2 lignes
  lcd.begin(16, 2);

  // Affiche 'Distance:' sur l'écran LCD (première ligne par défaut)
  lcd.print("Distance:");
  
}

void loop() {
  // Envoi d'une impulsion ultrasonique de 10 microsecondes sur la pin Trig
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Lecture du temps de trajet de l'onde sur la pin Echo
  duration = pulseIn(echoPin, HIGH);
  
  // Calcul de la distance en centimètres
  distanceCm = duration * 0.034 / 2;

  // Positionne le curseur de l'écran LCD sur la colonne 0, ligne 1 (deuxième ligne)
  lcd.setCursor(0, 1);

  // Affiche la valeur de la distance calculée
  lcd.print(distanceCm);

  // Affiche ' cm' à la suite (avec des espaces pour effacer les anciens chiffres plus longs)
  lcd.print(" cm      ");
  Serial.println(distanceCm);

  // Attend 500 ms avant de relever une nouvelle distance (tu peux ajuster si besoin)
  delay(1000);
}