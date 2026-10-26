import server


def test_public_leaderboard_shows_clubs_sorted_by_points(monkeypatch):
    monkeypatch.setattr(
        server,
        "clubs",
        [
            {"name": "Club Low", "email": "low@example.com", "points": "4"},
            {"name": "Club High", "email": "high@example.com", "points": "13"},
            {"name": "Club Middle", "email": "middle@example.com", "points": "12"},
        ],
    )

    response = server.app.test_client().get("/leaderboard")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Club High" in page
    assert "Club Middle" in page
    assert "Club Low" in page
    assert page.index("Club High") < page.index("Club Middle")
    assert page.index("Club Middle") < page.index("Club Low")
