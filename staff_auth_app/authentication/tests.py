const int ledPin1 = 13;
const int ledPin2 = 12; // Add the pin number for the second LED

void setup() {
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT); // Set the pin mode for the second LED
  Serial.begin(9600);  // Set the baud rate to 9600
}

void loop() {
  if (Serial.available() > 0) {
    char input = Serial.read();
    if (input == '1') {
      blinkLED(ledPin1); // Call blinkLED function for the first LED
    } else if (input == '0') {
      blinkLED2(ledPin2); // Call blinkLED function for the second LED
    }
  }
}

void blinkLED(int pin) { // Pass the pin number to blinkLED function
  // Rapid blink for 5 cycles
  for (int i = 0; i < 5; i++) {
    digitalWrite(pin, HIGH);
    delay(100);
    digitalWrite(pin, LOW);
    delay(100);
  }

  // Clear the input buffer (discard any additional characters)
  while (Serial.available() > 0) {
    Serial.read();
  }
}

void blinkLED2(int pin) { // Pass the pin number to blinkLED function
  // Rapid blink for 5 cycles
  for (int i = 0; i < 10; i++) {
    digitalWrite(pin, HIGH);
    delay(10);
    digitalWrite(pin, LOW);
    delay(10);
  }

  // Clear the input buffer (discard any additional characters)
  while (Serial.available() > 0) {
    Serial.read();
  }
}
