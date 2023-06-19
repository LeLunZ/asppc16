void setup() {
  Serial.begin(9600);
}

// the loop function runs over and over again forever
void loop() {
  Serial.write((byte) constrain(analogRead(A0)/2, 0, 255));
  delay(1000);
}
