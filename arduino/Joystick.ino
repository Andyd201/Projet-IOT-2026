// Déclaration des broches
const int joystick = 7;  // Bouton connecté à la broche D2
const int ledXPin = 2;    // LED pour l'axe X sur la broche D3
const int ledYPin = 4;    // LED pour l'axe Y sur la broche D4
const int xAxisPin = A0;  // Axe X du joystick connecté à A0
const int yAxisPin = A1;  // Axe Y du joystick connecté à A1

unsigned long previousMillis = 0;
const long interval = 100; // Envoi des données toutes les 100 ms

void setup() {
  // Configuration des broches
  pinMode(joystick, INPUT_PULLUP);
  pinMode(ledXPin, OUTPUT);
  pinMode(ledYPin, OUTPUT);
  
  // Éteindre les LED au démarrage
  digitalWrite(ledXPin, LOW);
  digitalWrite(ledYPin, LOW);

  // Initialisation du port série
  Serial.begin(9600);
}

void loop() {
  // ====================================================
  // 1. ÉCOUTE DES COMMANDES VENANT DE PYTHON
  // ====================================================
  if (Serial.available() > 0) {
    // Lire la ligne envoyée par Python jusqu'au retour à la ligne (\n)
    String commande = Serial.readStringUntil('\n');
    commande.trim(); // Supprime les espaces ou caractères invisibles

    // Exécution de l'action selon l'ordre reçu
    if (commande == "LEDX_ON") {
      digitalWrite(ledXPin, HIGH);
    } 
    else if (commande == "LEDX_OFF") {
      digitalWrite(ledXPin, LOW);
    } 
    else if (commande == "LEDY_ON") {
      digitalWrite(ledYPin, HIGH);
    } 
    else if (commande == "LEDY_OFF") {
      digitalWrite(ledYPin, LOW);
    } 
    else if (commande == "LEDS_OFF") {
      digitalWrite(ledXPin, LOW);
      digitalWrite(ledYPin, LOW);
    }
  }

  // ====================================================
  // 2. ENVOI DES DONNÉES À PYTHON (Régulé toutes les 100ms)
  // ====================================================
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    int buttonState = digitalRead(joystick);
    int xValue = analogRead(xAxisPin);
    int yValue = analogRead(yAxisPin);

    // Format strict attendu par le script Python
    Serial.print("BOUTON:");
    Serial.print(buttonState);
    Serial.print(",X:");
    Serial.print(xValue);
    Serial.print(",Y:");
    Serial.println(yValue); // .println ajoute le \n indispensable pour Python
  }
}
