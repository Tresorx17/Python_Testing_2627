import server


def test_unknown_email_shows_error_message():
    client = server.app.test_client()

    response = client.post(
        "/showSummary",
        data={"email": "unknown@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Adresse e-mail inconnue" in response.get_data(as_text=True)

def test_known_email_shows_summary():
    client = server.app.test_client()

    response = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "john@simplylift.co" in page
    assert "Spring Festival" in page