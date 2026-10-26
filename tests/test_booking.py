import pytest
import server


@pytest.mark.parametrize(
    "path",
    [
        "/book/Spring%20Festival/Unknown%20Club",
        "/book/Unknown%20Competition/Simply%20Lift",
    ],
)
def test_unknown_booking_reference_shows_error(path):
    client = server.app.test_client()
    response = client.get(path, follow_redirects=True)

    assert response.status_code == 200
    assert "introuvable" in response.get_data(as_text=True)

def test_booking_rejected_when_club_has_not_enough_points(monkeypatch):
    club = {"name": "Test Club", "email": "test@example.com", "points": "1"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert "Not enough points" in response.get_data(as_text=True)
    assert club["points"] == "1"
    assert competition["numberOfPlaces"] == "10"


def test_successful_booking_deducts_club_points(monkeypatch):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert club["points"] == "3"
    assert competition["numberOfPlaces"] == "8"
def test_booking_rejected_when_competition_has_too_few_places(monkeypatch):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "1",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={"club": "Test Club", "competition": "Test Competition", "places": "2"},
    )

    assert response.status_code == 200
    assert "Not enough places" in response.get_data(as_text=True)
    assert club["points"] == "5"
    assert competition["numberOfPlaces"] == "1"
@pytest.mark.parametrize("places", ["0", "-1"])
def test_booking_rejected_when_places_are_not_positive(monkeypatch, places):
    club = {"name": "Test Club", "email": "test@example.com", "points": "5"}
    competition = {
        "name": "Test Competition",
        "numberOfPlaces": "10",
        "date": "2030-01-01 10:00:00",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    response = server.app.test_client().post(
        "/purchasePlaces",
        data={
            "club": "Test Club",
            "competition": "Test Competition",
            "places": places,
        },
    )

    assert response.status_code == 200
    assert "positive number" in response.get_data(as_text=True)
    assert club["points"] == "5"
    assert competition["numberOfPlaces"] == "10"
