# 🚀 Déploiement Railway + GitHub

## Structure finale du repo GitHub

```
telegram-downloader/
├── app.py
├── requirements.txt
├── Procfile
├── railway.json
├── nixpacks.toml       ← installe ffmpeg automatiquement
├── .gitignore
└── templates/
    └── index.html
```

---

## Étape 1 — Mettre le projet sur GitHub

```bash
# Dans le dossier du projet
git init
git add .
git commit -m "Initial commit — TeleLoad"

# Créer un repo sur github.com puis :
git remote add origin https://github.com/TON_USERNAME/teleload.git
git push -u origin main
```

---

## Étape 2 — Déployer sur Railway

1. Aller sur **https://railway.app** → Se connecter avec GitHub
2. Cliquer **"New Project"**
3. Choisir **"Deploy from GitHub repo"**
4. Sélectionner votre repo `teleload`
5. Railway détecte automatiquement Python et lance le build

✅ C'est tout ! Railway génère une URL publique du type :
**https://teleload-production.up.railway.app**

---

## ⚠️ Point important — Stockage éphémère

Railway utilise un **système de fichiers éphémère** : les fichiers
téléchargés dans `downloads/` sont **perdus à chaque redéploiement**.

Ce n'est pas un problème car le flow est :
1. Utilisateur demande une vidéo
2. Le serveur la télécharge temporairement
3. L'utilisateur la récupère immédiatement via le bouton
4. Le fichier peut ensuite être supprimé

---

## Variables d'environnement (optionnel)

Dans Railway → votre projet → **Variables** :

| Variable | Valeur | Utilité |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `500` | Limite taille (optionnel) |
| `CLEANUP_MINUTES` | `30` | Durée avant suppression (optionnel) |

---

## Mises à jour

Chaque `git push` sur `main` redéploie automatiquement :

```bash
git add .
git commit -m "Mise à jour"
git push
```

Railway redémarre le service en quelques secondes.

---

## Mettre à jour yt-dlp (important !)

Telegram change régulièrement ses APIs. Pour forcer une mise à jour,
modifiez `requirements.txt` :

```
yt-dlp>=2024.1.1   →   yt-dlp  (sans version fixe = toujours la dernière)
```

Puis `git push` — Railway réinstalle la dernière version.
