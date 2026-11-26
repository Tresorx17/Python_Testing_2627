import json
from datetime import datetime, timedelta

import pytest

import server


def pytest_collection_modifyitems(items):
    """Classe automatiquement les tests selon leur dossier."""
    for item in items:
        parts = set(item.path.parts)
        if "unit" in parts:
            item.add_marker(pytest.mark.unitaire)
        elif "integration" in parts:
            item.add_marker(pytest.mark.integration)
        elif "functional" in parts:
            item.add_marker(pytest.mark.fonctionnel)


@pytest.fixture
def client(monkeypatch):
    """Client Flask de test, sans démarrer un serveur réseau."""
    monkeypatch.setitem(server.app.config, "TESTING", True)
    return server.app.test_client()


@pytest.fixture
def club_factory():
    """Fabrique des clubs indépendants pour chaque scénario."""
    def make_club(name="Test Club", email="test@example.com", points=20):
        return {"name": name, "email": email, "points": str(points)}

    return make_club


@pytest.fixture
def competition_factory():
    """Fabrique une compétition avec une date relative à aujourd’hui."""
    def make_competition(name="Test Competition", days=30, places=10):
        event_date = datetime.now() + timedelta(days=days)
        return {
            "name": name,
            "date": event_date.strftime("%Y-%m-%d %H:%M:%S"),
            "numberOfPlaces": str(places),
        }

    return make_competition


@pytest.fixture
def club(monkeypatch, club_factory):
    current = club_factory()
    monkeypatch.setattr(server, "clubs", [current])
    return current


@pytest.fixture
def competition(monkeypatch, competition_factory):
    current = competition_factory()
    monkeypatch.setattr(server, "competitions", [current])
    return current


@pytest.fixture
def isolated_json(monkeypatch, tmp_path):
    """Répertoire de données temporaire, pour ne jamais toucher aux JSON réels."""
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))

    def write(clubs=None, competitions=None):
        (tmp_path / "clubs.json").write_text(
            json.dumps({"clubs": clubs or []}), encoding="utf-8"
        )
        (tmp_path / "competitions.json").write_text(
            json.dumps({"competitions": competitions or []}), encoding="utf-8"
        )

    return tmp_path, write
