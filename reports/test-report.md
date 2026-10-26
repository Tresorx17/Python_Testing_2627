# Rapport de tests

**Date :** 26 octobre 2026  
**Environnement :** Windows, Python 3.13.17, Flask 1.1.2, pytest 9.1.1, coverage 7.17.0

## Résultats

- **16 tests réussis, 0 échec.**
- **Couverture du module applicatif `server.py` : 92 %.**
- Couverture totale du rapport pytest : 97 % (inclut aussi les modules de tests).
- Les 236 avertissements sont des avertissements de dépréciation émis par les dépendances Werkzeug et itsdangerous ; aucun n’a fait échouer un test.

## Fonctionnalités vérifiées

Connexion avec une adresse connue ou inconnue ; références de club/compétition invalides ; réservation réussie ; solde de points insuffisant ; compétition insuffisamment disponible ; quantité nulle ou négative ; limite de 12 places ; persistance JSON ; erreur d’écriture et restauration des valeurs ; chargement des fichiers JSON ; classement public ; disponibilité de la feuille CSS.

## Commande de vérification

```powershell
.\.venv313\Scripts\python.exe -m coverage run -m pytest -q --disable-warnings --basetemp .pytest-report-run
.\.venv313\Scripts\python.exe -m coverage report -m
```