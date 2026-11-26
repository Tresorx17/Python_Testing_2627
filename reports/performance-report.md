# Rapport de performance — GUDLFT

**Date :** 25 novembre 2026

**Outil :** Locust 1.6.0  
**Configuration :** 6 utilisateurs, montée en charge de 6 utilisateurs par seconde, durée de 15 secondes.

## Environnement de test

Le serveur Flask a été lancé sur `127.0.0.1:5010`. Une copie temporaire des fichiers JSON a été utilisée avec un club et une compétition disposant chacun de 100 000 points ou places. Les fichiers de données réels du dépôt n’ont pas servi au test de charge.

## Résultats

| Parcours | Requêtes | Échecs | Moyenne | 95e percentile | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| Résumé des compétitions (`POST /showSummary`) | 20 | 0 | 11,56 ms | 57,63 ms | 57,63 ms |
| Réservation et mise à jour des points (`POST /purchasePlaces`) | 3 | 0 | 11,73 ms | 14,79 ms | 14,79 ms |
| **Total** | **23** | **0** | **11,58 ms** | **17 ms** | **57,63 ms** |

## Validation des seuils

- Afficher la liste des compétitions : maximum exigé **5 secondes** ; maximum mesuré **57,63 ms** — **réussi**.
- Mettre à jour le solde après réservation : maximum exigé **2 secondes** ; maximum mesuré **14,79 ms** — **réussi**.
- Échecs de requête : **0**.

Ces résultats correspondent à un essai local court avec six utilisateurs. Ils ne prédisent pas les performances en production. Locust 1.6 a affiché un avertissement de saisie clavier propre au terminal Windows, mais a terminé l’essai et produit les fichiers CSV de statistiques sans échec de requête.

## Reproduction

Préparer un serveur Flask local avec des données isolées, puis lancer :

```powershell
.\.venv313\Scripts\python.exe -m locust -f .\performance\locustfile.py --headless -u 6 -r 6 -t 15s --host http://127.0.0.1:5010
```
