#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 2
#define RST_PIN 4
#define BUZZER 15

const char* ssid = "RRR";
const char* password = "987654321";
const char* serverURL = "http://172.24.15.57:5000/recipe"; // Replace with your PC WiFi IP ipconfig only 172.24.15.57 part

MFRC522 rfid(SS_PIN, RST_PIN);

String getRecipeType(String uid) {
  if (uid == "EA792303") return "vegetarian";
  if (uid == "73064A34") return "chicken";
  if (uid == "6EA5D505") return "quick";
  if (uid == "D3413230") return "Beef";
  if (uid == "63253030") return "fish";
  //if (uid == "63BB7934") return "Big fish";
  if (uid == "F3CD1D34") return "Healthy meal";
  if (uid == "03AFA234") return "Salad";
  return "general";
}

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 2);
  rfid.PCD_Init();
  
  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // Build UID string
  String uidStr = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";
    uidStr += String(rfid.uid.uidByte[i], HEX);
  }
  uidStr.toUpperCase();

  String recipeType = getRecipeType(uidStr);
  Serial.println("Recipe type: " + recipeType);

  // Buzzer beep
  digitalWrite(BUZZER, HIGH);
  delay(200);
  digitalWrite(BUZZER, LOW);

  // Send to Python server
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"type\":\"" + recipeType + "\"}";
    int code = http.POST(json);

    if (code > 0) {
      String recipe = http.getString();
      Serial.println("Recipe received:");
      Serial.println(recipe);
      Serial.println("-----------------------\n");
    } else {
      Serial.println("sending request");
    }

    http.end();
  }

  rfid.PICC_HaltA();
  delay(2000); // wait before next scan
}void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}
