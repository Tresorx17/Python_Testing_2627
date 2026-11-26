def test_home_page_is_available(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Portail des compétitions" in response.get_data(as_text=True)


def test_logout_returns_to_home_page(client):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
