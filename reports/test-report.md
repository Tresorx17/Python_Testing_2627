# Rapport de tests — GUDLFT

**Date :** 26 novembre 2026

**Environnement :** Windows, Python 3.13.17, Flask 1.1.2, pytest 9.1.1, pytest-cov 7.1.0, Selenium 4.54.0 et Locust 1.6.0.

## Résultats pytest

- **52 tests collectés : 48 réussis et 4 tests Selenium ignorés par l’environnement.** Aucun test exécuté n’a échoué.
- **Couverture de `server.py` : 100 % (160 instructions sur 160).**
- Lors de cette vérification, les 4 tests Selenium ont été ignorés parce que Chrome n’a pas pu démarrer une session dans l’environnement d’exécution. Ils ne sont donc pas comptés comme réussis ; ils restent à exécuter dans un environnement où le navigateur démarre correctement.
- Les avertissements restants sont des dépréciations provenant principalement des versions anciennes de Werkzeug et itsdangerous utilisées par le projet. Ils n’ont pas fait échouer les tests.

## Répartition

| Niveau | Nombre collecté | Résultat |
| --- | ---: | --- |
| Tests unitaires | 13 | 13 réussis |
| Tests d’intégration | 35 | 35 réussis |
| Tests fonctionnels Selenium | 4 | 4 ignorés car Chrome n’a pas démarré dans l’environnement de vérification |

Le guide recommande d’essayer d’écrire deux fois plus de tests unitaires que de tests d’intégration ou fonctionnels. La suite actuelle privilégie les tests d’intégration, car les exigences portent surtout sur les échanges entre routes Flask et fichiers JSON. La couverture complète de `server.py` est atteinte, mais l’équilibre numérique entre catégories reste à améliorer si le professeur applique ce ratio strictement.

## Résultats des tests de charge

Locust a été exécuté pendant 15 secondes avec 6 utilisateurs et une montée en charge de 6 utilisateurs par seconde, sur un serveur local et des données JSON temporaires.

| Parcours | Requêtes | Échecs | Moyenne | 95e percentile | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| Affichage du résumé (`POST /showSummary`) | 20 | 0 | 11,56 ms | 57,63 ms | 57,63 ms |
| Réservation (`POST /purchasePlaces`) | 3 | 0 | 11,73 ms | 14,79 ms | 14,79 ms |
| **Total** | **23** | **0** | **11,58 ms** | **17 ms** | **57,63 ms** |

Les deux seuils de la spécification sont respectés pendant cet essai local : moins de 5 secondes pour le résumé et moins de 2 secondes pour une réservation. Cet essai court avec six utilisateurs ne constitue pas une garantie de performance en production. Locust 1.6 a également affiché un avertissement de lecture clavier associé au terminal Windows ; les statistiques CSV ont été générées et ne signalent aucune requête en échec.

## Commandes

Tests et couverture :

```powershell
.\.venv313\Scripts\python.exe -m pytest --cov=server --cov-report=term-missing -rs
```

Tests unitaires et d’intégration seulement :

```powershell
.\.venv313\Scripts\python.exe -m pytest -m "not fonctionnel" --cov=server --cov-report=term-missing
```

Essai Locust à reproduire sur un serveur local isolé :

```powershell
.\.venv313\Scripts\python.exe -m locust -f .\performance\locustfile.py --headless -u 6 -r 6 -t 15s --host http://127.0.0.1:5010
```

Les scénarios et leurs résultats attendus figurent dans [le plan de test](plan-de-test.md).
