# Mise en ligne du site de Yeba chez Opalstack, pas à pas

Même méthode que data.cd, sur le même compte Opalstack, dans une application séparée. Remplacer partout `UTILISATEUR` par le nom de l'utilisateur shell et `opalX.opalstack.com` par l'adresse du serveur, et `yeba.cd` par le domaine retenu.

Installation essayée à blanc le 21/10/2026 (Python 3.13, environnement neuf, `.env` rempli, `DJANGO_DEBUG=0`) : `deployer.sh --premier` va jusqu'à « Terminé », `check --deploy` sans alerte, pages et fichiers statiques servis.

**Sans domaine pour l'instant ?** On peut tout installer dès maintenant sur l'adresse gratuite d'Opalstack (*Domains* : `yeba.UTILISATEUR.opalstacked.com`), puis ajouter le vrai domaine au site Opalstack et à `DJANGO_ALLOWED_HOSTS` le jour où il est réservé.

## A. Tableau de bord Opalstack

1. **Domaine.** *Domains* : ajouter `yeba.cd` et `www.yeba.cd` (ou l'adresse `opalstacked.com`). Chez le registraire du domaine, faire pointer les DNS vers Opalstack comme pour data.cd.
2. **Application Django.** *Applications → Add Application* : nom `yeba`, même utilisateur shell que data.cd, type **Django**. Opalstack crée `~/apps/yeba/` avec `env/`, `start`, `stop`, `uwsgi.ini` et un projet d'exemple `myproject/`.
3. **Application pour les images.** *Add Application* : nom `yeba_media`, type **Static Only**.
4. **Site.** *Sites → Add Site* : domaines de l'étape 1 ; routes `/` → `yeba` et `/media` → `yeba_media` ; cocher **Let's Encrypt** et **Redirect HTTP to HTTPS**.
5. **Boîte e-mail.** *Mail → Add Mailbox*, puis l'adresse `contact@yeba.cd` reliée à cette boîte. Noter le serveur SMTP, le nom de la boîte et son mot de passe. Ajouter les enregistrements SPF/DKIM proposés.

Pas besoin de PostgreSQL : SQLite suffit largement pour un site de présentation.

## B. Envoyer les fichiers

6. Récupérer `yeba-site.zip` (dans les fichiers du projet, dossier `yeba/site-web/`) et l'envoyer dans `~/apps/yeba/` :
   `scp yeba-site.zip UTILISATEUR@opalX.opalstack.com:~/apps/yeba/` (ou FileZilla, SFTP, port 22).

## C. Installer en SSH

7. **Se connecter et décompresser** :
   ```bash
   ssh UTILISATEUR@opalX.opalstack.com
   cd ~/apps/yeba && env/bin/python --version     # 3.10 ou plus récent
   unzip -o yeba-site.zip && rm yeba-site.zip
   touch ~/apps/yeba_media/essai && rm ~/apps/yeba_media/essai && echo OK
   ```
   Le dernier test doit afficher « OK » (sinon recréer `yeba_media` en **Static Only**, sans « Symbolic link »).
8. **Pointer uWSGI sur le site.** `nano ~/apps/yeba/uwsgi.ini`, remplacer les trois lignes qui mentionnent `myproject` par :
   ```ini
   python-path = /home/UTILISATEUR/apps/yeba/site
   wsgi-file = /home/UTILISATEUR/apps/yeba/site/config/wsgi.py
   touch-reload = /home/UTILISATEUR/apps/yeba/site/config/wsgi.py
   ```
   Enregistrer (Ctrl+O, Entrée, Ctrl+X), puis `rm -rf ~/apps/yeba/myproject`.
9. **Fichier des secrets** :
   ```bash
   cd ~/apps/yeba/site && cp .env.exemple .env && chmod 600 .env
   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   nano .env
   ```
   Coller la chaîne après `DJANGO_SECRET_KEY=` ; mettre `DJANGO_MEDIA_ROOT=/home/UTILISATEUR/apps/yeba_media` ; remplir `DJANGO_ALLOWED_HOSTS`, `DJANGO_SITE_URL`, les lignes `DJANGO_EMAIL_…` (étape 5) et `DJANGO_ADMINS` (qui reçoit les messages du formulaire).
10. **Installer** :
    ```bash
    bash deployer.sh --premier
    ```
    Le script sauvegarde la base, installe les dépendances, vérifie les réglages de sécurité, prépare les fichiers statiques, crée les tables et les pages de départ, puis redémarre. Il doit finir par « Terminé ».
11. **Premier compte d'administration** :
    ```bash
    ../env/bin/python manage.py createsuperuser
    ../env/bin/python manage.py sendtestemail vous@exemple.com
    ```
12. **Adresse du site.** Elle est reprise de `DJANGO_SITE_URL` à l'étape 10. Si le domaine change plus tard : `https://yeba.cd/admin/`, *Paramètres → Sites*, corriger le nom d'hôte (port `443`).

## D. Vérifier

13. `https://yeba.cd` s'affiche avec le cadenas ; `https://yeba.cd/sante/` répond `{"ok": true}` ; `/sitemap.xml` et `/robots.txt` répondent.
14. Envoyer un message depuis la page Contact : il arrive chez `DJANGO_ADMINS` et dans *Formulaires → Contact*.
15. Envoyer une image dans *Images* et l'afficher dans une page : cela confirme l'étape 7.
16. Remplir *Paramètres → Coordonnées et réseaux sociaux* et la liste « À compléter avant l'ouverture » du README.

## Mises à jour

Envoyer le nouveau zip comme à l'étape 6, le décompresser (`unzip -o`), puis `cd ~/apps/yeba/site && bash deployer.sh`. Le `.env`, la base et les images ne sont pas dans le zip et ne sont jamais écrasés.

## Sauvegardes

`deployer.sh` copie la base dans `sauvegardes/` à chaque mise à jour (14 dernières gardées). Pour une copie chaque nuit, `crontab -e` puis :

```
30 2 * * * cd ~/apps/yeba/site && cp db.sqlite3 sauvegardes/db_$(date +\%Y-\%m-\%d).sqlite3 && find sauvegardes -name 'db_*' -mtime +14 -delete
```

Les images sont dans `~/apps/yeba_media/`. Pour tout rapatrier sur un ordinateur : `scp -r UTILISATEUR@opalX.opalstack.com:~/apps/yeba/site/sauvegardes ./yeba-sauvegardes` et de même pour `yeba_media`.

**En cas d'erreur** : `tail -50 ~/apps/yeba/site/logs/django.log` et `tail -50 ~/logs/apps/yeba/uwsgi.log`.
