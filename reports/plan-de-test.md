# Plan de test — GUDLFT

**Version :** 1.0
**Date :** 26 novembre 2026
**But :** vérifier les bogues corrigés, les parcours existants et les fonctions ajoutées avant la remise.

## Périmètre et méthode

Le plan reprend le modèle fourni : chaque scénario comporte un identifiant, une action à vérifier, des données et un résultat attendu. Les préfixes distinguent le niveau de test : **UT** pour unitaire, **IT** pour intégration, **FT** pour fonctionnel avec Selenium et **PT** pour performance avec Locust.

Les essais utilisent des clubs et des compétitions temporaires. Ils ne doivent pas modifier les fichiers JSON réels du projet. Les tests unitaires vérifient une fonction isolée ; les tests d’intégration vérifient les échanges entre Flask, ses fonctions et les fichiers JSON ; les tests Selenium suivent les actions d’un utilisateur dans un navigateur.

## Adresses et méthodes à vérifier

| Adresse locale | Méthode | Utilité |
| --- | --- | --- |
| `http://127.0.0.1:5000/` | GET | Accueil et formulaire de connexion |
| `/showSummary` | POST | Connexion et affichage du résumé du club |
| `/book/<compétition>/<club>` | GET | Affichage du formulaire de réservation |
| `/purchasePlaces` | POST | Validation et enregistrement d’une réservation |
| `/leaderboard` | GET | Classement public des clubs |
| `/competitions/new` | GET, POST | Formulaire puis création d’une compétition |
| `/logout` | GET | Retour à l’accueil |
| `/static/style.css` | GET | Feuille de style |

Pour Selenium, le serveur de test utilise un port local libre au lieu du port 5000 afin d’éviter de dépendre d’un serveur déjà ouvert.

## Scénarios

| ID | Scénario | Données | Résultat attendu |
| --- | --- | --- | --- |
| UT01 | Convertir une date de compétition valide | `2030-01-01 10:00:00` | La date est convertie sans erreur. |
| UT02 | Refuser une date mal formée ou absente | Texte invalide, chaîne vide, date absente | La fonction signale une erreur de format contrôlée. |
| UT03 | Déterminer si une compétition est passée | Une date passée, une date future et une date invalide | Passée : vrai ; future : faux ; date invalide : traitée sans plantage. |
| UT04 | Séparer et trier les compétitions | Événements passés, futurs et date invalide | Les événements futurs sont triés par date croissante ; les passés restent dans l’historique. |
| UT05 | Enregistrer un fichier JSON de façon atomique | Objet JSON temporaire | Le fichier contient exactement les nouvelles données et aucun fichier temporaire ne reste. |
| UT06 | Gérer une erreur d’écriture atomique | Échec simulé du remplacement ou de la création temporaire | L’erreur est remontée et le fichier temporaire est nettoyé lorsqu’il existe. |
| IT01 | Se connecter avec l’adresse connue | `john@simplylift.co`, `POST /showSummary` | Réponse 200, espace du club affiché avec ses compétitions. |
| IT02 | Refuser une adresse inconnue | `unknown@example.com`, `POST /showSummary` | Retour à l’accueil et message d’adresse inconnue ; aucune erreur serveur. |
| IT03 | Ouvrir une réservation valide | Compétition future et club connus, `GET /book/...` | Réponse 200 et formulaire de réservation affiché. |
| IT04 | Réserver des places disponibles | 2 places, solde 20, capacité 10, `POST /purchasePlaces` | Confirmation ; solde à 18 et capacité à 8 dans les données temporaires. |
| IT05 | Refuser une quantité supérieure au solde | 2 places demandées, 1 point | Message d’erreur ; solde et capacité inchangés. |
| IT06 | Refuser une quantité supérieure à la capacité | 2 places demandées, 1 place disponible | Message d’erreur ; solde et capacité inchangés. |
| IT07 | Refuser une quantité nulle, négative ou non numérique | `0`, `-1`, `beaucoup` | Message de validation ; données inchangées. |
| IT08 | Appliquer le plafond de réservation | 13 places demandées | Réservation refusée ; solde et capacité inchangés. |
| IT09 | Empêcher une réservation passée | Compétition datée dans le passé | Message explicatif ; impossible de réserver par l’écran ou par requête directe. |
| IT10 | Gérer les références inconnues | Club ou compétition inconnus | Retour contrôlé à l’accueil avec un message ; pas de code 500. |
| IT11 | Persister une réservation dans les JSON | Réservation valide sur répertoire temporaire | Les points et les places mis à jour sont relus dans les deux fichiers JSON. |
| IT12 | Gérer l’échec de sauvegarde d’une réservation | Répertoire temporaire inaccessible | Message d’échec ; les valeurs en mémoire reviennent à leur état initial. |
| IT13 | Créer un événement valide | Nom inédit, date future, 24 places | Confirmation et événement ajouté au fichier JSON. |
| IT14 | Refuser les données d’événement incorrectes | Nom vide ou doublon, date invalide/passée, capacité nulle | Message adapté ; aucun nouvel événement ajouté. |
| IT15 | Gérer l’échec de sauvegarde d’un événement | Écriture JSON simulée en échec | Message d’erreur ; liste en mémoire inchangée. |
| IT16 | Consulter le classement public | Clubs avec 4, 12 et 13 points | Réponse 200, classement décroissant ; la page ne demande pas de connexion. |
| IT17 | Gérer un classement vide et la déconnexion | Aucun club ; `GET /logout` | Message informatif pour le classement vide ; déconnexion redirige vers l’accueil. |
| IT18 | Charger les pages et le CSS | `GET /` et `GET /static/style.css` | Réponse 200 ; contenu et feuille de style présents. |
| FT01 | Se connecter dans le navigateur | E-mail valide, formulaire de l’accueil | Selenium affiche l’espace du club et sa compétition. |
| FT02 | Refuser une adresse dans le navigateur | E-mail inconnue | Le message de validation apparaît dans la page. |
| FT03 | Effectuer une réservation dans le navigateur | 2 places sur une compétition future | Message de confirmation ; les JSON temporaires reflètent les nouveaux soldes. |
| FT04 | Créer une compétition dans le navigateur | Nom inédit, date future, 30 places | Confirmation visible et événement enregistré. |
| PT01 | Charger le résumé de compétitions en charge | 6 utilisateurs, `POST /showSummary` | Aucune erreur ; réponse inférieure à 5 secondes selon le guide fonctionnel. |
| PT02 | Enregistrer des réservations en charge | 6 utilisateurs, `POST /purchasePlaces` | Aucune erreur ; mise à jour inférieure à 2 secondes selon le guide fonctionnel. |

## Vérification et validation

- **Vérification :** pytest contrôle les réponses HTTP, les messages, les valeurs en mémoire et les données JSON temporaires ; Coverage indique les lignes exécutées ; Locust mesure les temps et les erreurs.
- **Validation :** les résultats attendus sont comparés aux exigences de la spécification fonctionnelle : connexion, réservation, absence de surréservation, plafond de 12 places, classement public, création et organisation des compétitions.
- **Critère minimal de couverture :** au moins 60 % selon le guide du projet ; l’objectif visé est une couverture complète de `server.py`.
- **Critère de performance :** 6 utilisateurs ; moins de 5 secondes pour l’affichage des compétitions et moins de 2 secondes pour une mise à jour de réservation.

## Exécution

Depuis la racine du dépôt, dans PowerShell :

```powershell
.\.venv313\Scripts\python.exe -m pytest --cov=server --cov-report=term-missing -rs
```

Les parcours Selenium nécessitent un navigateur compatible et un pilote WebDriver autorisé par Windows. Les essais Locust sont lancés séparément contre une copie de l’application avec des données isolées.
