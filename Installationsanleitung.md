# Projekt Setup
Zunächst muss die jeweilige Applikation im Terminal geöffnet werden, um anschließend die notwendigen Befehle ausführen zu können.


![Struktur](https://github.com/user-attachments/assets/b7c0fccd-bc6f-4872-a090-35eb5455c3eb)

## Server

#### 1. Virtuelles Verzeichnis (Virtual Environment – venv) erstellen:  
Isolierte Python-Umgebung, um Abhängigkeiten getrennt vom System zu verwalten
```bash
python3 -m venv venv
```

#### 2. venv aktivieren
Aktiviert das virtuelle Verzeichnis, damit alle nachfolgenden Python-Befehle in dieser Umgebung ausgeführt werden
```bash
source venv/bin/activate
```

#### 3. flask installieren
Installiert Flask-Framework für den Aufbau des Servers
```bash
pip install flask
```

#### 4. flask_cors installieren
Installiert Flask-CORS-Bibliothek, um vom Frontend sicher auf die API des Backends zuzugreifen
```bash
pip install flask_cors
```


#### 5. SQLAlchemy installieren
Installiert SQLAlchemy, um die Python-Objekte direkt mit den Datenbanktabellen zu verknüpfen
```bash
pip install sqlalchemy
```


#### 6. bcrypt installieren
Installiert bcrypt, für das sichere Passwort-Hashing und -Verifizierung
```bash
pip install bcrypt
```


#### 7. Server starten
Startet den Server mit der angegebenen Python-Datei
```bash
python server/app.py
```


## Client
Um auch den Client ausführen zu können, ist es hier von Vorteil erneut ein Terminal Fenster für die jeweilige Applikation zu öffnen.

#### 1. Verzeichnis wechseln
In das Client-Verzeichnis wechseln, um den Frontend-Code auszuführen
```bash
cd client
```


#### 2. Abhängigkeiten installieren
Installiert alle im Projekt definierten Abhängigkeiten
```bash
npm install
```


#### 3. Client starten
Startet das Frontend
```bash
npm run dev
```
