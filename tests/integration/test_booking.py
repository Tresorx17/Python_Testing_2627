import json
import pytest
import server


def test_past_competition_shows_message_and_hides_booking_link(monkeypatch, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2020-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/showSummary", data={"email": "test@example.com"}
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Désolé, cet événement est passé" in page
    assert "Book Places" not in page


def test_past_competition_cannot_be_booked_directly(monkeypatch, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2020-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Test Club",
            "competition": "Test Competition",
            "places": "2",
        },
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Désolé, cet événement est passé" in page
    assert club["points"] == "5"
    assert competition["numberOfPlaces"] == "10"


@pytest.mark.parametrize(
    "path",
    [
        "/book/Spring%20Festival/Unknown%20Club",
        "/book/Unknown%20Competition/Simply%20Lift",
    ],
)
def test_unknown_booking_reference_shows_error(path, client):
    response = client.get(path, follow_redirects=True)

    assert response.status_code == 200
    assert "introuvable" in response.get_data(as_text=True)

def test_booking_rejected_when_club_has_not_enough_points(monkeypatch, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "1"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert "Points insuffisants" in response.get_data(as_text=True)
    assert club["points"] == "1"
    assert competition["numberOfPlaces"] == "10"


def test_successful_booking_deducts_club_points(monkeypatch, tmp_path, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert club["points"] == "3"
    assert competition["numberOfPlaces"] == "8"
def test_booking_rejected_when_competition_has_too_few_places(monkeypatch, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "1",
        "date": "2030-01-01 10:00:00",
    }
    
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert "Nombre de places insuffisant" in response.get_data(as_text=True)
    assert club["points"] == "5"
    assert competition["numberOfPlaces"] == "1"
@pytest.mark.parametrize("places", ["0", "-1"])
def test_booking_rejected_when_places_are_not_positive(monkeypatch, places, tmp_path, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))
    (tmp_path / "clubs.json").write_text(
        json.dumps({"clubs": [club]}), encoding="utf-8"
    )
    (tmp_path / "competitions.json").write_text(
        json.dumps({"competitions": [competition]}), encoding="utf-8"
    )
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Test Club",
            "competition": "Test Competition",
            "places": places,
        },
    )

    assert response.status_code == 200

    assert "supérieur à zéro" in response.get_data(as_text=True)
    assert club["points"] == "5"
    assert competition["numberOfPlaces"] == "10"
def test_successful_booking_saves_changes_to_json(monkeypatch, tmp_path, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))
    (tmp_path / "clubs.json").write_text(
        json.dumps({"clubs": [club]}), encoding="utf-8"
    )
    (tmp_path / "competitions.json").write_text(
        json.dumps({"competitions": [competition]}), encoding="utf-8"
    )
    
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    saved_clubs = json.loads((tmp_path / "clubs.json").read_text(encoding="utf-8"))
    saved_competitions = json.loads(
        (tmp_path / "competitions.json").read_text(encoding="utf-8")
    )

    assert response.status_code == 200
    assert saved_clubs["clubs"][0]["points"] == "3"
    assert saved_competitions["competitions"][0]["numberOfPlaces"] == "8"
def test_booking_rejected_above_twelve_places(monkeypatch, tmp_path, client):
    club = {"name": "Test Club", "email": "test@example.com", "points": "13"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "25",
        "date": "2030-01-01 10:00:00",
    }

    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    (tmp_path / "clubs.json").write_text(
        json.dumps({"clubs": [club]}), encoding="utf-8"
    )
    (tmp_path / "competitions.json").write_text(
        json.dumps({"competitions": [competition]}), encoding="utf-8"
    )

    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Test Club",
            "competition": "Test Competition",
            "places": "13",
        },
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "au maximum 12 places" in page
    assert club["points"] == "13"
    assert competition["numberOfPlaces"] == "25"
def test_booking_save_failure_does_not_change_points_or_places(
    monkeypatch, tmp_path, client
):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }

    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path / "missing"))
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert "n’a pas pu être enregistrée" in response.get_data(as_text=True)
    assert club["points"] == "5"
    assert competition["numberOfPlaces"] == "10"


def test_booking_rejects_unknown_references(client, monkeypatch, club_factory):
    monkeypatch.setattr(server, "clubs", [club_factory()])
    monkeypatch.setattr(server, "competitions", [])

    response = client.post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Missing", "places": "1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "introuvable" in response.get_data(as_text=True)


def test_booking_rejects_non_numeric_quantity(client, monkeypatch, club, competition):
    response = client.post(
        "/purchasePlaces",
        data={
            "club": club["name"],
            "competition": competition["name"],
            "places": "beaucoup",
        },
    )

    assert response.status_code == 200
    assert "données de réservation valides" in response.get_data(as_text=True)
    assert club["points"] == "20"
    assert competition["numberOfPlaces"] == "10"


def test_get_booking_for_past_event_returns_message(client, monkeypatch, club_factory, competition_factory):
    past_event = competition_factory(days=-3)
    monkeypatch.setattr(server, "clubs", [club_factory()])
    monkeypatch.setattr(server, "competitions", [past_event])

    response = client.get(
        "/book/Test%20Competition/Test%20Club", follow_redirects=True
    )

    assert response.status_code == 200
    assert "cet événement est passé" in response.get_data(as_text=True)


def test_upcoming_competition_opens_booking_form(client, club, competition):
    response = client.get(
        "/book/Test%20Competition/Test%20Club"
    )

    assert response.status_code == 200
    assert "Test Competition" in response.get_data(as_text=True)
    assert 'name="places"' in response.get_data(as_text=True)

