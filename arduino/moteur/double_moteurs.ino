// Robot 2 moteurs - Arduino Motor Shield Rev3
// Moteur GAUCHE = bornier A (A- / A+)
// Moteur DROIT  = bornier B (B- / B+)

// Pins du shield (fixes)
const int DIR_A = 12, PWM_A = 3,  BRAKE_A = 9;
const int DIR_B = 13, PWM_B = 11, BRAKE_B = 8;

const int VITESSE = 255;  // 0 à 255

void setup() {
  pinMode(DIR_A, OUTPUT);
  pinMode(BRAKE_A, OUTPUT);
  pinMode(DIR_B, OUTPUT);
  pinMode(BRAKE_B, OUTPUT);
  arreter();
  delay(2000);
}

void loop() {
  avancer();        delay(1500);
  arreter();        delay(500);
  reculer();        delay(1500);
  arreter();        delay(500);
  tournerGauche();  delay(800);
  arreter();        delay(500);
  tournerDroite();  delay(800);
  arreter();        delay(2000);
}

// Moteur gauche (A) : true = avant, false = arrière
void gauche(bool avant) {
  digitalWrite(BRAKE_A, LOW);
  digitalWrite(DIR_A, avant ? HIGH : LOW);
  analogWrite(PWM_A, VITESSE);
}

// Moteur droit (B) : true = avant, false = arrière
void droite(bool avant) {
  digitalWrite(BRAKE_B, LOW);
  digitalWrite(DIR_B, avant ? HIGH : LOW);
  analogWrite(PWM_B, VITESSE);
}

void avancer()       { gauche(true);  droite(true);  }
void reculer()       { gauche(false); droite(false); }
void tournerGauche() { gauche(false); droite(true);  }
void tournerDroite() { gauche(true);  droite(false); }

void arreter() {
  digitalWrite(BRAKE_A, HIGH);
  digitalWrite(BRAKE_B, HIGH);
  analogWrite(PWM_A, 0);
  analogWrite(PWM_B, 0);
}