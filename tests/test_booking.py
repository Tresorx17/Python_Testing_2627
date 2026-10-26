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