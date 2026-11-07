const byte LED_GAUCHE = 2;
const byte LED_DROITE = 3;

void traiterCommande(String commande) {
  commande.trim();

  if (commande == "G_ON") {
    digitalWrite(LED_GAUCHE, HIGH);
  } else if (commande == "G_OFF") {
    digitalWrite(LED_GAUCHE, LOW);
  } else if (commande == "D_ON") {
    digitalWrite(LED_DROITE, HIGH);
  } else if (commande == "D_OFF") {
    digitalWrite(LED_DROITE, LOW);
  } else if (commande.length() > 0) {
    Serial.println("ERR");
  }
}

void setup() {
  pinMode(LED_GAUCHE, OUTPUT);
  pinMode(LED_DROITE, OUTPUT);
  digitalWrite(LED_GAUCHE, LOW);
  digitalWrite(LED_DROITE, LOW);

  Serial.begin(9600);
}

void loop() {
  while (Serial.available() > 0) {
    String commande = Serial.readStringUntil('\n');
    traiterCommande(commande);
  }
}
