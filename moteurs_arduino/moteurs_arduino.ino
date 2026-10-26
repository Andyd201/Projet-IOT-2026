/*
  moteurs_arduino.ino - L'Arduino pilote le L298N, le Raspberry Pi envoie les ordres par USB (série).

  Branchement Arduino Uno -> L298N :
    D5  -> ENA (PWM, vitesse moteur A)   | enlever le jumper ENA
    D7  -> IN1
    D8  -> IN2
    D6  -> ENB (PWM, vitesse moteur B)   | enlever le jumper ENB
    D9  -> IN3
    D10 -> IN4
    GND -> GND du L298N (masse commune avec l'alim des moteurs)

  Raspberry Pi <-> Arduino : simple câble USB (alimente l'Arduino + communication).

  Protocole (une commande par ligne, 115200 bauds) :
    A <vitesse>   moteur A, vitesse de -255 à 255 (négatif = arrière)   ex: A 150
    B <vitesse>   moteur B                                               ex: B -200
    M <a> <b>     les deux moteurs d'un coup                             ex: M 150 150
    S             stop tout (roue libre)
    F             freinage actif des deux moteurs
    P             ping -> répond "PONG"
  Réponse "OK" après chaque commande valide, "ERR" sinon.
*/

const int ENA = 5, IN1 = 7, IN2 = 8;
const int ENB = 6, IN3 = 9, IN4 = 10;

// Sécurité : si aucune commande reçue pendant ce délai, on arrête les moteurs.
// 0 = désactivé. Mets par ex. 1000 si ton Pi envoie des ordres en continu.
const unsigned long TIMEOUT_MS = 0;

unsigned long derniereCommande = 0;
String ligne = "";

void setMoteur(int en, int inA, int inB, int vitesse) {
  vitesse = constrain(vitesse, -255, 255);
  if (vitesse > 0) {
    digitalWrite(inA, HIGH);
    digitalWrite(inB, LOW);
  } else if (vitesse < 0) {
    digitalWrite(inA, LOW);
    digitalWrite(inB, HIGH);
  } else {
    digitalWrite(inA, LOW);
    digitalWrite(inB, LOW);
  }
  analogWrite(en, abs(vitesse));
}

void stopTout() {
  setMoteur(ENA, IN1, IN2, 0);
  setMoteur(ENB, IN3, IN4, 0);
}

void freiner() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, HIGH); analogWrite(ENA, 255);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, HIGH); analogWrite(ENB, 255);
}

void traiter(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  char c = toupper(cmd.charAt(0));
  String args = cmd.substring(1);
  args.trim();

  if (c == 'A') {
    setMoteur(ENA, IN1, IN2, args.toInt());
  } else if (c == 'B') {
    setMoteur(ENB, IN3, IN4, args.toInt());
  } else if (c == 'M') {
    int esp = args.indexOf(' ');
    if (esp < 0) { Serial.println("ERR"); return; }
    setMoteur(ENA, IN1, IN2, args.substring(0, esp).toInt());
    setMoteur(ENB, IN3, IN4, args.substring(esp + 1).toInt());
  } else if (c == 'S') {
    stopTout();
  } else if (c == 'F') {
    freiner();
  } else if (c == 'P') {
    Serial.println("PONG");
    derniereCommande = millis();
    return;
  } else {
    Serial.println("ERR");
    return;
  }

  derniereCommande = millis();
  Serial.println("OK");
}

void setup() {
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  stopTout();
  Serial.begin(115200);
  Serial.println("PRET");
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') {
      traiter(ligne);
      ligne = "";
    } else if (ch != '\r' && ligne.length() < 32) {
      ligne += ch;
    }
  }

  if (TIMEOUT_MS > 0 && millis() - derniereCommande > TIMEOUT_MS) {
    stopTout();
  }
}
