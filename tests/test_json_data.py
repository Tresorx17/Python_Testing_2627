import json
import server


def test_load_clubs_uses_application_data_directory(monkeypatch, tmp_path):
    expected_clubs = [
        {"name": "Test Club", "email": "test@example.com", "points": "5"}
    ]
    (tmp_path / "clubs.json").write_text(
        json.dumps({"clubs": expected_clubs}), encoding="utf-8"
    )
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))

    assert server.loadClubs() == expected_clubs


def test_load_competitions_uses_application_data_directory(
    monkeypatch, tmp_path
):
    expected_competitions = [
        {
            "name": "Test Competition",
            "date": "2030-01-01 10:00:00",
            "numberOfPlaces": "10",
        }
    ]
    (tmp_path / "competitions.json").write_text(
        json.dumps({"competitions": expected_competitions}), encoding="utf-8"
    )
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))

    assert server.loadCompetitions() == expected_competitions