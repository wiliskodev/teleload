# 🚀 Guide de Déploiement — TeleLoad

Téléchargeur de vidéos Telegram (Application Web)

---

## 📁 Structure du projet

```
telegram-downloader/
├── app.py               ← Backend Flask (serveur)
├── requirements.txt     ← Dépendances Python
├── templates/
│   └── index.html       ← Interface web
└── downloads/           ← Créé automatiquement (vidéos temporaires)
```

---

## ⚙️ Option A — Lancer en local (votre PC)

### Prérequis

- Python 3.10+ installé → https://python.org
- `ffmpeg` installé (nécessaire pour fusionner audio+vidéo)

### 1. Installer ffmpeg

**Windows :**
```
winget install ffmpeg
```
ou télécharger sur https://ffmpeg.org/download.html et ajouter au PATH

**macOS :**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian) :**
```bash
sudo apt install ffmpeg -y
```

---

### 2. Installer les dépendances Python

```bash
cd telegram-downloader
python -m venv venv

# Activer l'environnement virtuel
# Windows :
venv\Scripts\activate
# macOS / Linux :
source venv/bin/activate

pip install -r requirements.txt
```

---

### 3. Lancer l'application

```bash
python app.py
```

Ouvrez votre navigateur sur → **http://localhost:5000**

---

## ☁️ Option B — Déploiement sur un VPS (Serveur en ligne)

> Recommandé pour un accès permanent depuis n'importe où.
> Fournisseurs recommandés : **Hetzner** (€4/mois), **DigitalOcean**, **OVH**

### 1. Se connecter au VPS

```bash
ssh root@VOTRE_IP_SERVEUR
```

### 2. Installer les dépendances système

```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv ffmpeg nginx -y
```

### 3. Copier le projet sur le serveur

**Depuis votre PC :**
```bash
scp -r telegram-downloader/ root@VOTRE_IP:/opt/teleload/
```

Ou cloner depuis Git si vous avez mis le projet sur GitHub :
```bash
git clone https://github.com/VOUS/teleload /opt/teleload
```

### 4. Installer les dépendances Python

```bash
cd /opt/teleload
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configurer Gunicorn (serveur de production)

Créer le fichier service systemd :
```bash
nano /etc/systemd/system/teleload.service
```

Coller ce contenu :
```ini
[Unit]
Description=TeleLoad Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/teleload
Environment="PATH=/opt/teleload/venv/bin"
ExecStart=/opt/teleload/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer et démarrer :
```bash
systemctl daemon-reload
systemctl enable teleload
systemctl start teleload
systemctl status teleload   # vérifier que ça tourne
```

### 6. Configurer Nginx (proxy web)

```bash
nano /etc/nginx/sites-available/teleload
```

```nginx
server {
    listen 80;
    server_name VOTRE_DOMAINE_OU_IP;

    client_max_body_size 2G;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    location /downloads/ {
        alias /opt/teleload/downloads/;
        add_header Content-Disposition "attachment";
    }
}
```

```bash
ln -s /etc/nginx/sites-available/teleload /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

Votre app est accessible sur → **http://VOTRE_IP**

---

### 7. Ajouter HTTPS (SSL gratuit avec Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d votre-domaine.com
```

✅ Votre app est maintenant sur → **https://votre-domaine.com**

---

## 🔄 Nettoyage automatique des fichiers

Pour éviter de remplir le disque, ajoutez un cron job :

```bash
crontab -e
```

Ajouter :
```
0 * * * * find /opt/teleload/downloads/ -mmin +60 -delete
```

→ Supprime les vidéos téléchargées depuis plus d'1 heure.

---

## ⚠️ Limitations importantes

| Limitation | Détail |
|---|---|
| **Vidéos privées** | Ne fonctionnent pas sans authentification Telegram |
| **Canaux privés** | Inaccessibles sans session Telegram |
| **Taille max** | Limitée par l'espace disque du serveur |
| **Vitesse** | Dépend de la connexion du serveur |

### Pour les vidéos privées (avancé)

Si vous voulez télécharger vos propres vidéos privées, vous pouvez
exporter votre session Telegram et configurer yt-dlp :

```bash
# Générer un fichier de cookies Telegram
yt-dlp --cookies-from-browser chrome "URL_PRIVEE"
```

---

## 🛠️ Dépannage

**`yt-dlp` non trouvé :**
```bash
pip install -U yt-dlp
```

**Erreur ffmpeg :**
```bash
which ffmpeg   # doit retourner un chemin
ffmpeg -version
```

**Port 5000 déjà utilisé :**
```bash
lsof -i :5000
kill -9 PID
```

**Mettre à jour yt-dlp (important, Telegram change souvent) :**
```bash
yt-dlp -U
# ou
pip install -U yt-dlp
```

---

## 📝 Notes légales

- Usage personnel uniquement
- Respectez les droits d'auteur
- Ne pas redistribuer du contenu protégé
- Respectez les CGU de Telegram
