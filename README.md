# SMART-COOK-AI_TUI_PROJECT
An interactive Human-Computer Interaction (HCI) project that combines:

1. Google Gemini AI (recipe generation)

2. Text-to-Speech (gTTS + pygame)

3. Automated step timers

4. Flask backend API

5. Tkinter desktop UI

6. Designed for RFID-triggered interaction

This system generates dynamic, step-by-step cooking recipes with automatic timers and voice guidance — creating a hands-free smart cooking experience.

# 🚀 Project Overview

The Smart RFID Cooking Assistant allows users to:

📇 Scan a Recipe Card → AI generates a new recipe

⏭ Scan a Next Step Card → Moves to next cooking step
  or, scan other recipe cards(recipe card can be modified according user intrest like fish, mutton recipe card)

🔔 Automatic timer per step

🗣 Voice instruction playback

🖥 Live UI with countdown + progress bar

This project was developed as part of an HCI course project focusing on tangible interaction using RFID-based input.

# 🛠 Technologies Used

🔌 Hardware & Embedded

ESP32 Microcontroller

Arduino IDE (for ESP32 programming)

RFID Module ( MFRC522)

RFID Cards 

WiFi Communication

Buzzer

Jumper Wires

Breadboard

# 📡 Setup
 MFRC522 Pin | ESP32 Pin 
 ----------- | --------- 
 SDA (SS)    | GPIO 2    
 SCK         | GPIO 18   
 MOSI        | GPIO 23   
 MISO        | GPIO 19   
 RST         | GPIO 4    
 GND         | GND       
 3.3V        | 3.3V      

| Buzzer Pin   | ESP32   |
| ------------ | ------- |
| + (Positive) | GPIO 15 |
| – (Negative) | GND     |
    
1. After connecting the wires connect with the pc through USB cable.Then first of all open the RFID_Card_Number.ino on the arduino ide and scan the cards id number and note it down.(Ensure that necessary Esp32 package and Rfid packes is downloaded on arduino ide)
  
2. now inject the Arduino_Esp32_main.ino to ESP-32

 ***In code segment input the ssid(wifi name) and  wifi password***
 
 ***Make your your pc and ESP-32 connected on same network***
 
 


 ***In cmd type "ipconfig" and copy the ip addrees in avobe pic and put it to the RFID_Card_Number.ino serverURL option***

3.Make sure to install python and its necessary libary file. Open cmd_main.py 

<


***Here in the code edit api_key with your own API key string. Save the file***

***Now go to the location of cmd_main.py and open cmd and type "python cmd_main.py " to run the code.***

***All is done. Our project is ready. Scan the desired RFID card to see the output***

<
![WhatsApp Image 2026-02-16 at 10 08 05 PM](https://github.com/user-attachments/assets/8342108d-544b-4484-9138-c2683acbc0e9)
![WhatsApp Image 2026-02-16 at 10 08 04 PM](https://github.com/user-attachments/assets/7f1adb78-f7bb-49b4-bf8f-d3ed8cfb45e6)

Screenshot 2026-01-25 130715Screenshot 2026-01-26 181218Screenshot 2026-01-26 181403Screenshot 2026-01-26 182200
WhatsApp Image 2026-02-16 at 10 08 05 PM WhatsApp Image 2026-02-16 at 10 08 04 PM
