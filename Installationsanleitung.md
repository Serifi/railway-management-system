# Installationsanleitung
Anfangs muss die jeweilige Applikation im Terminal geöffnet werden, um die notwendigen Befehle ausführen zu können.

> [!NOTE]  
> Voraussetzung für die Ausführung ist eine, vorzugsweise globale, Installation von **Python 3.13** und **Node 23.1.0**
> 
> **Python**: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
> **Node**: [https://nodejs.org/en/download](https://nodejs.org/en/download)

## Server

#### 1. Virtuelles Verzeichnis (Virtual Environment – venv) erstellen:  
Erstellung einer isolierten Python-Umgebung, um Abhängigkeiten getrennt vom System zu verwalten
```bash
python3 -m venv venv
```

#### 2. venv aktivieren
Aktivierung des virtuellen Verzeichnis, um alle nachfolgenden Befehle in dieser Umgebung auszuführen
```bash
source venv/bin/activate
```

#### 3. flask installieren
Installation von Flask, um den Server aufzubauen
```bash
pip install flask
```

#### 4. flask_cors installieren
Installation von Flask-CORS, um vom Frontend sicher auf die API des Backends zuzugreifen
```bash
pip install flask_cors
```
#### 5. flask_migrate installieren
```bash
pip install flask_migrate
```

#### 6. requests installieren
```bash
pip install requests
```

#### 7. SQLAlchemy installieren
Installation von SQLAlchemy, um die Python-Objekte mit den Datenbanktabellen zu verknüpfen
```bash
pip install sqlalchemy
```

```bash
pip install flask_sqlalchemy
```

#### 8. bcrypt installieren
Installation von bcrypt, um die Passwörter zu verschlüsseln
```bash
pip install bcrypt
```

#### 9. flask_swagger_ui installieren
Installation von swagger_ui zur Dokumentation der Endpunkte
```bash
pip install flask_swagger_ui
```

#### 9. Server starten
Start des Servers
```bash
python server/app.py
```

## Client
Um auch den Client ausführen zu können, ist es hier von Vorteil erneut ein Terminal für die jeweilige Applikation zu öffnen.

#### 1. Verzeichnis wechseln
Man muss in das Verzeichnis des Clients wechseln, um das Frontend auszuführen
```bash
cd client
```

#### 2. Abhängigkeiten installieren
Installation aller im Projekt festgelegten Abhängigkeiten
```bash
npm install
```

#### 3. Client starten
Start des Clients
```bash
npm run dev
```
