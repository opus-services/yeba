# Site de l'ASBL Yeba

Site de présentation de l'association : qui elle est, ses projets, son agenda d'activités, ses actualités, comment la soutenir et la contacter. Tout se modifie dans une administration en français, sans toucher au code.

- Mise en ligne chez Opalstack : [MISE-EN-LIGNE.md](MISE-EN-LIGNE.md)
- Captures du site et de l'administration : dossier `captures/`

## Pourquoi Wagtail

Le site utilise **Wagtail**, un CMS libre et gratuit construit sur Django, le même socle que data.cd.

- **Même hébergeur, même méthode.** Il s'installe chez Opalstack exactement comme data.cd (application Django, fichier `.env`, script `deployer.sh`). Pas de nouvel outil à apprendre ni de nouvel abonnement.
- **Simple pour la rédaction.** L'administration est en français, les pages se composent par blocs (texte, image, citation, chiffres clés, bouton, document, vidéo), avec brouillon, aperçu avant publication, historique des versions et publication programmée.
- **Peu d'entretien.** Pas d'extensions à mettre à jour une par une, contrairement à WordPress, qui est la cible de la plupart des piratages de sites associatifs. Une mise à jour = changer un numéro de version dans `requirements.txt` puis `bash deployer.sh`.
- **Séparé de data.cd.** Code, base et domaine distincts : une panne ou une mise à jour de l'un ne touche pas l'autre.

Les deux autres options sérieuses : WordPress (plus connu des bénévoles, mais extensions à suivre et failles fréquentes) et un site statique avec Decap CMS (rien à entretenir côté serveur, mais chaque rédacteur a besoin d'un compte GitHub et la publication passe par un dépôt). Wagtail est le meilleur compromis ici parce que l'équipe sait déjà héberger un projet Django.

## Ce que contient le site

| Rubrique | Type de page | Ce qu'on y fait |
|---|---|---|
| Accueil | Page d'accueil | Bandeau « Savoir pour agir », 4 axes d'action, projets, 3 prochaines activités, 3 dernières actualités, partenaires, appel à soutenir |
| Qui sommes-nous | Page simple | Mission, objectifs, principes (tirés des statuts) ; sous-page **Gouvernance** |
| Nos projets | Liste + fiches projet | data.cd, Yeba Réflexion, Yeba Éditions ; statut, site, lancement, activités et actualités liées |
| Activités | Agenda + fiches | Conférences, séminaires, ateliers, tables rondes, formations, campagnes, actions de terrain ; à venir et passées, filtre par type, lien d'inscription |
| Actualités | Liste + articles | Date, auteur, projet concerné, pagination |
| Nous soutenir | Page simple | Devenir membre, rejoindre le réseau, partenariats, dons (bouton orange de l'en-tête) |
| Contact | Formulaire | Nom, e-mail, téléphone, objet, message ; envoi par e-mail et archive dans l'administration ; piège à robots |
| Mentions légales | Page simple | Lien en pied de page |

Aussi : recherche sur tout le site, plan du site (`/sitemap.xml`), `robots.txt`, aperçus soignés sur WhatsApp et Facebook (titre, résumé, image), site adapté au téléphone, page d'erreur 404.

La charte « Le Fleuve » est appliquée : bleu fleuve `#0E5266`, orange couchant pour les appels à agir, nuit équatoriale pour le pied de page, sable pour les fonds ; titres en Unbounded 600, texte en Figtree, dates et chiffres en JetBrains Mono ; logo B « la foule » dans l'en-tête, symbole A « le signal » comme icône d'onglet. Le nom s'écrit « yeba » dans le logotype, « Yeba » dans les textes ; « Yeba! » n'apparaît que comme appel, au-dessus du titre de l'accueil.

## Guide de la rédaction

L'administration est à l'adresse `/admin/` du site.

**Publier une activité.** *Pages → Accueil → Activités → Ajouter une page enfant.* Remplir le type, les dates, le lieu, un chapeau de deux ou trois phrases et une image, puis *Publier*. Elle apparaît d'elle-même sur l'accueil (si elle est parmi les trois prochaines) et dans l'agenda. Après l'événement, rouvrir la même page pour ajouter le compte rendu, les photos et les documents : elle passe seule dans « Activités passées ».

**Publier une actualité.** *Pages → Accueil → Actualités → Ajouter une page enfant.* Même principe ; le champ « Projet concerné » la fait aussi apparaître sur la fiche du projet.

**Ajouter un projet.** *Pages → Accueil → Nos projets → Ajouter une page enfant.* Décocher « Afficher sur l'accueil » pour qu'il n'apparaisse que dans la liste.

**Composer le contenu.** Le champ « Contenu » se remplit bloc par bloc avec le bouton **+** : texte, intertitre, image, citation, chiffres clés, encadré, bouton, document à télécharger, vidéo YouTube ou Facebook (coller simplement le lien).

**Brouillon, aperçu, programmation.** *Enregistrer le brouillon* garde la page sans la montrer ; l'icône d'aperçu montre le rendu ; dans le menu du bouton vert, *Programmer la publication* la met en ligne à la date choisie.

**Menu du site.** Une page de premier niveau apparaît dans le menu si la case *Afficher dans les menus* (onglet *Promotion*) est cochée. L'ordre du menu suit l'ordre des pages dans *Pages → Accueil* (glisser-déposer).

**Coordonnées et réseaux sociaux.** *Paramètres → Coordonnées et réseaux sociaux* : adresse, e-mail, téléphone, WhatsApp, liens Facebook, X, LinkedIn, YouTube, Instagram, TikTok. Ils s'affichent en pied de page dès qu'ils sont remplis.

**Partenaires.** *Fragments → Partenaires* : nom, logo, lien. Ils s'affichent sur l'accueil (« Ils nous accompagnent »).

**Messages reçus.** *Formulaires → Contact* : tous les messages, exportables en tableur. Ils sont aussi envoyés par e-mail aux adresses indiquées dans la page Contact (onglet *Contenu*, en bas).

**Comptes de l'équipe.** *Paramètres → Utilisateurs → Ajouter un utilisateur.* Groupe **Editors** pour publier, **Moderators** pour valider les publications des autres. Pour qu'un bénévole propose sans publier, créer un groupe avec le seul droit « Ajouter » et activer un *workflow* de validation (*Paramètres → Workflows*).

**Photos.** Envoyer des images d'au moins 1 600 pixels de large ; le site fabrique seul les tailles nécessaires. Cliquer sur la photo dans *Images* pour placer le point d'intérêt (le visage, par exemple) : les recadrages le garderont.

## Développement en local

```bash
python3 -m venv env && env/bin/pip install -r requirements.txt
env/bin/python manage.py migrate
env/bin/python manage.py peupler_yeba --exemples   # pages de départ + activités d'exemple
env/bin/python manage.py createsuperuser
env/bin/python manage.py runserver                 # http://localhost:8000 et /admin/
env/bin/python manage.py test site_yeba            # 8 tests
```

`peupler_yeba` crée les pages de départ sans jamais modifier une page qui existe déjà. L'option `--exemples` ajoute quatre activités et une actualité fictives : **jamais sur le site en ligne**.

## Organisation du code

```
config/            réglages (lus dans .env), adresses, WSGI
site_yeba/
  models.py        types de pages, coordonnées, partenaires
  blocks.py        blocs du champ « Contenu »
  templates/       gabarits des pages et des blocs
  static/yeba/     feuille de style de la charte, logos SVG
  management/commands/peupler_yeba.py   pages de départ
  tests.py
templates/         base commune, 404, 500, habillage Yeba de l'administration
deployer.sh        installation et mises à jour sur le serveur
```

## À compléter avant l'ouverture

- Domaine (`yeba.cd` ou `yeba.org`) et boîte `contact@…`
- Adresse du siège et directeur de la publication dans *Mentions légales*
- Coordonnées et réseaux sociaux dans *Paramètres*
- Photos : bandeau de l'accueil, projets, activités
- Coordonnées de dons dans *Nous soutenir* quand les comptes seront ouverts
- Composition des organes dans *Gouvernance* après l'assemblée constitutive
