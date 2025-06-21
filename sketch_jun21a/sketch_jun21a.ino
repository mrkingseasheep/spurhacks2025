#include <Servo.h>

int VRX_PIN = A0;

Servo myservo;
int servoPin = 4;
float pos = 0;
int xVal;

void setup() {
  Serial.begin(9600);
  pinMode(2, OUTPUT);
  myservo.attach(servoPin);
  Serial.print("Hiiii");
}
/***
void loop() {
  digitalWrite(2,HIGH);
  delay(300);

  digitalWrite(2,LOW);
  delay(700);

  
}
***/

void loop() {
  xVal = analogRead(VRX_PIN);
  Serial.println(xVal);
  float scaled = (xVal - 500) / 500;
  pos += scaled;
  myservo.write(pos);
  delay(15);
}