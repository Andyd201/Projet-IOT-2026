/*
  moteurs_arduino.ino - L'Arduino pilote le L293D, le Raspberry Pi envoie les ordres par USB (série).

  Un seul moteur, sur OUT1 / OUT2 du L293D (broches 3 et 6).
  Branchement Arduino Uno -> L293D :
    D3 -> IN1 (broche 2, PWM : règle la vitesse)
    D4 -> IN2 (broche 7, pas PWM : sens seulement)
    +5V -> EN1,2 (broche 1), VCC1 (broche 16) et VCC2 (broche 8)
    GND -> broches 4, 5, 12, 13 du L293D (masse commune avec l'Arduino)
  Si le moteur tourne dans le mauvais sens, mettre INVERSER à true.

  Bouton ON/OFF de l'auto :
    D7 -> une patte du bouton, GND -> l'autre patte (pas de résistance, on utilise le pull-up interne)
  Chaque appui allume / éteint l'auto. Au démarrage, l'auto est éteinte.

  Raspberry Pi <-> Arduino : simple câble USB (alimente l'Arduino + communication).

  Protocole (une commande par ligne, 115200 bauds) :
    A <vitesse>   moteur, vitesse de -255 à 255 (négatif = arrière)      ex: A 150
    M <a> <b>     compatibilité : seul <a> est utilisé                   ex: M 150 150
    B <vitesse>   compatibilité : ignoré (pas de moteur B)
    S             stop (roue libre)
    F             freinage actif
    E             état -> répond "ETAT ON" ou "ETAT OFF"
    P             ping -> répond "PONG"
  Réponse "OK" après chaque commande valide, "ERR" sinon.
  A / B / M répondent "OFF" (et le moteur reste arrêté) si l'auto est éteinte.
  À chaque appui sur le bouton, l'Arduino envoie de lui-même "ETAT ON" ou "ETAT OFF".
*/

// D3 est PWM (vitesse), D4 ne l'est pas (sens). Ne pas les échanger.
const int PWM = 3, SENS = 4;

// Mettre à true si le moteur tourne à l'envers (au lieu d'inverser les fils).
const bool INVERSER = false;

const int BOUTON = 7;
const unsigned long ANTI_REBOND_MS = 30;

bool autoOn = false;
bool boutonAppuye = false;
unsigned long dernierChangementBouton = 0;

// Sécurité : si aucune commande reçue pendant ce délai, on arrête le moteur.
// 0 = désactivé. Mets par ex. 1000 si ton Pi envoie des ordres en continu.
const unsigned long TIMEOUT_MS = 0;

unsigned long derniereCommande = 0;
unsigned long dernierCaractere = 0;
String ligne = "";

void setMoteur(int vitesse) {
  vitesse = constrain(vitesse, -255, 255);
  if (INVERSER) vitesse = -vitesse;
  if (vitesse > 0) {
    digitalWrite(SENS, LOW);
    analogWrite(PWM, vitesse);
  } else if (vitesse < 0) {
    // SENS à HIGH, donc on inverse le PWM pour garder la même échelle de vitesse
    digitalWrite(SENS, HIGH);
    analogWrite(PWM, 255 + vitesse);
  } else {
    digitalWrite(PWM, LOW);
    digitalWrite(SENS, LOW);
  }
}

void stopTout() {
  setMoteur(0);
}

void freiner() {
  digitalWrite(PWM, HIGH);
  digitalWrite(SENS, HIGH);
}

void envoyerEtat() {
  Serial.println(autoOn ? "ETAT ON" : "ETAT OFF");
}

void lireBouton() {
  bool appuye = digitalRead(BOUTON) == LOW;
  if (appuye == boutonAppuye || millis() - dernierChangementBouton < ANTI_REBOND_MS) return;
  boutonAppuye = appuye;
  dernierChangementBouton = millis();
  if (!appuye) return;  // on bascule à l'appui, pas au relâchement

  autoOn = !autoOn;
  if (!autoOn) stopTout();
  envoyerEtat();
}

void traiter(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  char c = toupper(cmd.charAt(0));
  String args = cmd.substring(1);
  args.trim();

  if (!autoOn && (c == 'A' || c == 'B' || c == 'M')) {
    stopTout();
    Serial.println("OFF");
    return;
  }

  if (c == 'A') {
    setMoteur(args.toInt());
  } else if (c == 'B') {
    // pas de moteur B
  } else if (c == 'M') {
    int esp = args.indexOf(' ');
    if (esp < 0) { Serial.println("ERR"); return; }
    setMoteur(args.substring(0, esp).toInt());
  } else if (c == 'S') {
    stopTout();
  } else if (c == 'F') {
    freiner();
  } else if (c == 'P') {
    Serial.println("PONG");
    derniereCommande = millis();
    return;
  } else if (c == 'E') {
    envoyerEtat();
    return;
  } else {
    Serial.println("ERR");
    return;
  }

  derniereCommande = millis();
  Serial.println("OK");
}

void setup() {
  pinMode(PWM, OUTPUT); pinMode(SENS, OUTPUT);
  pinMode(BOUTON, INPUT_PULLUP);
  stopTout();
  Serial.begin(115200);
  Serial.println("PRET");
}

void loop() {
  lireBouton();

  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') {
      traiter(ligne);
      ligne = "";
    } else if (ch != '\r' && ligne.length() < 32) {
      ligne += ch;
    }
    dernierCaractere = millis();
  }

  // Moniteur série sans fin de ligne (ex. Tinkercad) : on exécute après 50 ms sans rien recevoir
  if (ligne.length() > 0 && millis() - dernierCaractere > 50) {
    traiter(ligne);
    ligne = "";
  }

  if (TIMEOUT_MS > 0 && millis() - derniereCommande > TIMEOUT_MS) {
    stopTout();
  }
}
