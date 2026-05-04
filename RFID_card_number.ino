#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 2
#define RST_PIN 4

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);

  // SPI pins for ESP32 (SCK, MISO, MOSI, SS)
  SPI.begin(18, 19, 23, 2);

  rfid.PCD_Init();
  Serial.println("Scan an RFID card...");
}

void loop() {

  // Look for new card
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  Serial.print("Card UID: ");

  String uidStr = "";

  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      Serial.print("0");
      uidStr += "0";
    }

    Serial.print(rfid.uid.uidByte[i], HEX);
    uidStr += String(rfid.uid.uidByte[i], HEX);
  }

  uidStr.toUpperCase();

  Serial.println();
  Serial.println("UID String: " + uidStr);
  Serial.println("-----------------------");

  rfid.PICC_HaltA();
  delay(1500);
}void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}
