Installation der D*Lite Applikation (see English Version below)
===================================================================
Voraussetzung: Raspberry Model 3B+ oder 4B mit 
  - Raspbian Buster oder Raspberry Pi OS Buster (Legacy) mit
  - Python 3.7.3 oder höher
  - Lego Mindstorms EV3

Empfohlen: Update von Raspbian/Pi OS Buster
- sudo apt update
- sudo apt full-upgrade

Die Installation der D*Lite Applikation besteht aus:

1) Anmeldung als user "pi". 

2) Optional: Zugriff auf den Pi über VNC von einem PC aus:
   https://www.raspberrypi.org/documentation/remote-access/vnc/README.md
   
3) Zusätzlichen Bluetooth-Manager installieren:
      - Bluetooth Manager installieren
          - sudo apt-get install bluetooth bluez blueman
      - Bluetooth Name anpassen:
         sudo nano /etc/machine-info
         Folgende Zeile einfügen dann sichern und schließen:
         PRETTY_HOSTNAME=pi4robo
      - Raspberry Pi neu starten
      - Jetzt sollten zwei Bluetooth Icons (neu und alt) in der 
        Startleiste zu sehen sein. 
   
4) Einmaliges Bluetooth Pairing von Raspbery Pi und EV3-Stein
      - EV3-Stein: Im Menü Einstellungen:
          - Eintrag "Visibility" aktivieren
          - Eintrag "Bluetooth" aktivieren
          - Auf dem Display wird oben links ein BT-Icon und direkt 
            daneben ein "<" angezeigt.
          - EV3 ausschalten
      - Raspberry Pi: Pairing einleiten
          -  Altes Bluetooth Icon anklicken
          -  "Make Discoverable" anklicken
          -  EV3 einschalten 
          -  Altes Bluetooth Menu:
             - "Add Device" auswählen und kurz warten 
             - EV3-Stein auswählen und "Pair" klicken
             - EV3: Pairing bestätigen
             - EV3: Schnell 1234 eingeben (falls es nicht schon angezeigt wird)
                    und schnell bestätigen
             - Pi: Schnell 1234 in Dialog eingeben und schnell ok klicken 
             - Pi: Meldung "Pairing successfully"             
5) Serielle Bluetooth Verbindung einrichten
       - Nach jedem Booten neu einrichten!
       - Altes Bluetooth-Icon: Make Discovearable anklicken
       - EV3 einschalten
       - Neuen BT-Manager anklicken
       - Eintrag "Geräte" (Devices) anklicken
       - Der EV3-Stein ist nach erfolgreichem Pairing in der
         Liste der BT-Geräte enthalten.
       - EV3-Stein auswählen und "Einrichten" (Setup) auswählen
       - Option "Connect to serial port" auswählen
       - Klick "Weiter (Next)"
       - Eine Erfolgsmeldung sollte nun angezeigt werden.
       - Fenster schließen. 
       - EV3-Stein: Auf dem Display wird oben links ein BT-Icon und direkt 
         daneben "<" und ">" angezeigt. Im Raspberry Pi ist /etc/rfcomm0 vorhanden.
                    
6) Download des GitHub-Repository 
   auf dem Raspberry Pi unter dem user "pi":
   https://github.com/robodhhb/Interactive-D-Star-Lite
   und auch auf einem PC mit Verbindung zum EV3-Roboter

7) PC: Lego Mindstorms Projekt "PathRunner_V1.ev3" auf den Roboter laden.

8) Pi: LXTerminal öffnen und zip-Datei mit unzip in einem Ordner Ihrer Wahl entpacken
    und in den Ordner "Interactive-D-Star-Lite" mit cd wechseln

9) Programme starten:
    - Auf dem EV3 Roboter: main im Projekt PathRunner_V1.ev3
    - Auf dem Raspberry Pi: python3 DStarLiteMain.py
      
------------------    
Bekannte Probleme:
  - Der EV3-Roboter sollte immer mit frischen Batterien oder geladenem Akku betrieben werden.
  - Bedenken Sie, dass die Motoren des  PathRunner rückwärts drehen, wenn er vorwärts fährt.
    Ist dies bei Ihrem Roboter nicht so, verwenden Sie für beide Motoren 
	den „Invert Motor Block“. 
    
========================English Version====================================
Installation of the application "Interactive D*Lite"
----------------------------------------------------
Prerequisite: Raspberry Pi 3 Model B+ or 4B with:
   - Raspbian Buster or Raspberry Pi OS Buster (Legacy) with
   - Python 3.7.3 or higher
   - Lego Mindstorms EV3
   
Recommended: Update Raspbian/Pi OS Buster
- sudo apt update
- sudo apt full-upgrade

Installation steps:
   
1) Login as user "pi". 

2) Optional: Access the Pi desktop with VNC via a PC:
   https://www.raspberrypi.org/documentation/remote-access/vnc/README.md

3) Install additional Bluetooth-Manager:
    - Install Bluetooth-Manager with:
       - sudo apt-get install bluetooth bluez blueman
    - Change Bluetooth name:
       sudo nano /etc/machine-info
       Add the following line and save/close editor:
       PRETTY_HOSTNAME=pi4robo
    - Reboot Raspberry Pi
    - Now you should see two bluetooth icons: The new and the old one
    
4) One-time job: BT-Pairing of Raspberry Pi and EV3 
      - EV3: Menu Settings:
          - Check "Visibility"
          - Check  "Bluetooth"
          - On the EV3-Display you see a BT-Icon and a "<"
          - Switch off EV3
      - Raspberry Pi: Initiate pairing
          - Click on the "old" BT-Icon
          - Select "Make Discoverable"
          - Switch on EV3
          - Old Bluetooth Icon:
              - Select "Add Device" and wait until it shows your EV3
              - Select EV3 and click "Pair"
              - On EV3: Confirm pairing
              - On EV3: Quickly enter 1234 (if it is not already displayed)
                         and confirm quickly
              - On Pi: Quickly enter 1234 in the dialog and quickly enter OK
              - On Pi: Message "Pairing successfully"

5) Configure serial BT connection
      - Configure after each booting
      - Click on the "old" BT-Icon
          - Select "Make Discoverable"
      - Switch on EV3
      - Click on new BT-Manager
      - Select menu entry "Devices"
      - EV3 is listed
      - Select your EV3 and select "Setup"
      - Select option "Connect to serial port"
      - Click "Next"
      - A success message is displayed.
      - Close Window
      - On EV3: On display you see at the top a BT-icon and "<>". 
      - On Pi: /etc/rfcomm0  is present.

6) Download the GitHub-Repository 
   on the Raspberry Pi under the user "pi":
   https://github.com/robodhhb/Interactive-D-Star-Lite
   and also on a PC with connection to the EV3-robot

7) PC: Load EV3-project "PathRunner_V1.ev3" on the EV3
   
8) On Pi: Open LXTerminal and unzip downloaded file in a folder of your choice
   
9) Change directory to "Interactive-D-Star-Lite" and run the programs:
       - On EV3: Start main in project "PathRunner_V1.ev3"
       - On Pi:  python3 DStarLiteMain.py
 
--------------       
Known issues:
  - Please run the robot allways with fresh batteries or loaded accumulator.
  - Keep in mind that the PathRunner's motors are spinning backwards
    when it is moving forward. If this is not the case with your robot, 
	use the "Invert Motor Block" for both motors.
 
      
   

