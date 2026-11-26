import json

import pytest

import server


@pytest.mark.parametrize(
    "date_text",
    ["2030/01/01 10:00:00", "not-a-date", ""],
)
def test_competition_date_rejects_invalid_formats(date_text):
    with pytest.raises(ValueError):
        server.competitionDate({"date": date_text})


def test_competition_date_rejects_missing_date():
    with pytest.raises(KeyError):
        server.competitionDate({})


def test_competition_is_marked_past_when_date_is_in_the_past():
    assert server.competitionHasPassed(
        {"date": "2020-01-01 10:00:00"}
    ) is True


def test_competition_is_not_past_when_date_is_in_the_future(competition_factory):
    assert server.competitionHasPassed(competition_factory(days=30)) is False


@pytest.mark.parametrize("competition", [{}, {"date": None}, {"date": "bad"}])
def test_invalid_competition_date_is_safely_classified_as_past(competition):
    assert server.competitionHasPassed(competition) is True


def test_competitions_are_sorted_and_invalid_dates_are_kept_in_past(
    competition_factory,
):
    items = [
        competition_factory(name="Later", days=20),
        {"name": "Malformed", "numberOfPlaces": "5"},
        competition_factory(name="Earlier", days=5),
        competition_factory(name="Past", days=-5),
    ]

    upcoming, past = server.splitCompetitions(items)

    assert [item["name"] for item in upcoming] == ["Earlier", "Later"]
    assert {item["name"] for item in past} == {"Past", "Malformed"}


def test_atomic_json_save_writes_expected_content(tmp_path):
    destination = tmp_path / "data.json"

    server.saveJsonAtomically(str(destination), {"clubs": [{"name": "Club"}]})

    assert json.loads(destination.read_text(encoding="utf-8")) == {
        "clubs": [{"name": "Club"}]
    }
    assert list(tmp_path.iterdir()) == [destination]


def test_atomic_json_save_removes_temporary_file_after_replace_error(
    monkeypatch, tmp_path
):
    def fail_replace(_source, _destination):
        raise OSError("replace failed")

    monkeypatch.setattr(server.os, "replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        server.saveJsonAtomically(str(tmp_path / "data.json"), {"value": 1})

    assert list(tmp_path.iterdir()) == []


def test_atomic_json_save_propagates_temporary_file_creation_error(
    monkeypatch, tmp_path
):
    def fail_create(*_args, **_kwargs):
        raise OSError("cannot create temporary file")

    monkeypatch.setattr(server.tempfile, "NamedTemporaryFile", fail_create)

    with pytest.raises(OSError, match="cannot create temporary file"):
        server.saveJsonAtomically(str(tmp_path / "data.json"), {"value": 1})
