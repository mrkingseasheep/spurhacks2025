const int xPin = A0;  // Joystick X-axis connected to A0
const int yPin = A1;  // Joystick Y-axis connected to A1

unsigned long lastSendTime = 0;
const int interval = 20; // 20ms = 50 updates per second

void setup() {
  Serial.begin(9600);
}

void loop() {
  unsigned long now = millis();
  if (now - lastSendTime >= interval) {
    int x = analogRead(xPin);
    int y = analogRead(yPin);

    Serial.print(x);
    Serial.print(",");
    Serial.print(y);
    Serial.print('\n');

    lastSendTime = now;
  }
}
