# Rapport de performance

**Date :** 26 octobre 2026  
**Outil :** Locust 1.6.0  
**Configuration :** 6 utilisateurs simultanés, montée en charge de 6 utilisateurs/seconde, durée de 15 secondes.

Le test a utilisé une copie locale isolée de l’application avec des données JSON de test (100 000 points et 100 000 places) afin de ne pas modifier les données du projet. Le serveur Flask de développement tournait sur la même machine que Locust.

## Résultats

| Parcours | Requêtes | Échecs | Moyenne | 95e percentile | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| Afficher le résumé et la liste des compétitions (`POST /showSummary`) | 95 | 0 | 8,4 ms | 12 ms | 18,3 ms |
| Effectuer une réservation et enregistrer les points (`POST /purchasePlaces`) | 17 | 0 | 12,6 ms | 15 ms | 14,8 ms |
| **Total** | **112** | **0** | **9,0 ms** | **13 ms** | **18,3 ms** |

## Critères du guide

- Liste des compétitions : maximum 5 secondes ; résultat mesuré maximal 18,3 ms — **réussi**.
- Mise à jour du solde : maximum 2 secondes ; résultat mesuré maximal 14,8 ms — **réussi**.

Ces mesures décrivent uniquement un essai local de 15 secondes sur le serveur de développement avec six utilisateurs. Elles ne représentent pas une garantie de performance en production.

## Reproduction

Démarrer le serveur Flask de la copie isolée avec les fichiers de données de test, puis lancer :

```powershell
.\.venv313\Scripts\python.exe -m locust -f .\performance\locustfile.py --headless -u 6 -r 6 -t 15s --host http://127.0.0.1:5010
```