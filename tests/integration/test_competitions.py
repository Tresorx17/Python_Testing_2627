import json
from datetime import datetime, timedelta

import pytest

import server


def make_competition(name, days_from_now, places="10"):
    event_date = datetime.now() + timedelta(days=days_from_now)
    return {
        "name": name,
        "date": event_date.strftime("%Y-%m-%d %H:%M:%S"),
        "numberOfPlaces": places,
    }


def test_new_competition_form_is_available(client):
    response = client.get("/competitions/new")

    assert response.status_code == 200
    assert "Créer un événement" in response.get_data(as_text=True)


def test_new_competition_is_saved_to_json(monkeypatch, isolated_json, client):
    existing = make_competition("Existing Event", 60)
    monkeypatch.setattr(server, "competitions", [existing.copy()])
    tmp_path, write_json = isolated_json
    write_json(competitions=[existing])
    event_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M")

    response = client.post(
        "/competitions/new",
        data={"name": "Spring Cup", "date": event_date, "places": "24"},
    )

    saved = json.loads(
        (tmp_path / "competitions.json").read_text(encoding="utf-8")
    )["competitions"]
    assert response.status_code == 200
    assert "Événement ajouté avec succès" in response.get_data(as_text=True)
    assert saved[-1]["name"] == "Spring Cup"
    assert saved[-1]["numberOfPlaces"] == "24"
    assert len(server.competitions) == 2


def test_new_competition_rejects_duplicate_name(monkeypatch, isolated_json, client):
    existing = make_competition("Spring Cup", 60)
    monkeypatch.setattr(server, "competitions", [existing.copy()])
    isolated_json[1](competitions=[existing])

    response = client.post(
        "/competitions/new",
        data={
            "name": " spring cup ",
            "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M"),
            "places": "5",
        },
    )

    assert response.status_code == 200
    assert "porte déjà ce nom" in response.get_data(as_text=True)
    assert len(server.competitions) == 1


def test_new_competition_rejects_past_date_and_nonpositive_places(monkeypatch, client):
    monkeypatch.setattr(server, "competitions", [])
    past_response = client.post(
        "/competitions/new",
        data={
            "name": "Past Event",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "places": "5",
        },
    )
    zero_places_response = client.post(
        "/competitions/new",
        data={
            "name": "No Seats Event",
            "date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M"),
            "places": "0",
        },
    )

    assert "doit être dans le futur" in past_response.get_data(as_text=True)
    assert "supérieur à zéro" in zero_places_response.get_data(as_text=True)
    assert server.competitions == []


def test_upcoming_events_are_sorted_and_past_events_are_grouped_last():
    items = [
        make_competition("Later", 20),
        make_competition("Earlier", 5),
        make_competition("Past", -5),
    ]

    upcoming, past = server.splitCompetitions(items)

    assert [item["name"] for item in upcoming] == ["Earlier", "Later"]
    assert [item["name"] for item in past] == ["Past"]


def test_new_competition_rejects_an_empty_name(client, monkeypatch):
    monkeypatch.setattr(server, "competitions", [])
    response = client.post(
        "/competitions/new",
        data={"name": "  ", "date": "2030-01-01T10:00", "places": "5"},
    )

    assert "nom de l’événement est obligatoire" in response.get_data(as_text=True)


@pytest.mark.parametrize(
    ("date_text", "places_text", "expected_message"),
    [
        ("pas-une-date", "5", "date et un nombre de places valides"),
        ("2030-01-01T10:00", "abc", "date et un nombre de places valides"),
        ("2030-01-01T10:00", "0", "supérieur à zéro"),
    ],
)
def test_new_competition_rejects_invalid_date_or_capacity(
    client, monkeypatch, date_text, places_text, expected_message
):
    monkeypatch.setattr(server, "competitions", [])
    response = client.post(
        "/competitions/new",
        data={"name": "Invalid Event", "date": date_text, "places": places_text},
    )

    assert expected_message in response.get_data(as_text=True)
    assert server.competitions == []


def test_new_competition_save_failure_does_not_add_it_in_memory(
    client, monkeypatch, competition_factory
):
    existing = competition_factory()
    monkeypatch.setattr(server, "competitions", [existing])

    def fail_save(*_args, **_kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(server, "saveJsonAtomically", fail_save)
    event_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M")
    response = client.post(
        "/competitions/new",
        data={"name": "New Cup", "date": event_date, "places": "12"},
    )

    assert "n’a pas pu être enregistré" in response.get_data(as_text=True)
    assert server.competitions == [existing]
