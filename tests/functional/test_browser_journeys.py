import json
import threading
from datetime import datetime, timedelta

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import make_server

import server


@pytest.fixture
def live_server(monkeypatch, tmp_path, club_factory, competition_factory):
    club = club_factory()
    competition = competition_factory()
    (tmp_path / "clubs.json").write_text(
        json.dumps({"clubs": [club]}), encoding="utf-8"
    )
    (tmp_path / "competitions.json").write_text(
        json.dumps({"competitions": [competition]}), encoding="utf-8"
    )
    monkeypatch.setattr(server, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])

    http_server = make_server("127.0.0.1", 0, server.app, threaded=True)
    worker = threading.Thread(target=http_server.serve_forever, daemon=True)
    worker.start()
    yield {
        "url": f"http://127.0.0.1:{http_server.server_port}",
        "data_dir": tmp_path,
        "club": club,
        "competition": competition,
    }
    http_server.shutdown()
    worker.join(timeout=5)


@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1365,900")
    try:
        driver = webdriver.Chrome(options=options)
    except (OSError, WebDriverException) as error:
        pytest.skip(
            "Impossible de démarrer une session Chrome dans cet environnement "
            f"({error.__class__.__name__})."
        )
    driver.implicitly_wait(3)
    yield driver
    driver.quit()


def test_browser_login_displays_club_dashboard(browser, live_server):
    browser.get(live_server["url"])
    browser.find_element(By.ID, "email").send_keys("test@example.com")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    heading = WebDriverWait(browser, 10).until(
        conditions.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    assert "Test Club" in heading.text
    assert "Test Competition" in browser.page_source


def test_browser_rejects_unknown_email(browser, live_server):
    browser.get(live_server["url"])
    browser.find_element(By.ID, "email").send_keys("unknown@example.com")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    message = WebDriverWait(browser, 10).until(
        conditions.visibility_of_element_located((By.CLASS_NAME, "messages"))
    )
    assert "Adresse e-mail inconnue" in message.text


def test_browser_booking_updates_points_and_available_places(browser, live_server):
    browser.get(live_server["url"])
    browser.find_element(By.ID, "email").send_keys("test@example.com")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    booking_link = WebDriverWait(browser, 10).until(
        conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, ".event-card a.button-outline")
        )
    )
    booking_link.click()
    places = browser.find_element(By.ID, "places")
    places.send_keys("2")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(browser, 10).until(
        conditions.text_to_be_present_in_element(
            (By.CLASS_NAME, "messages"), "Réservation confirmée"
        )
    )
    saved_clubs = json.loads(
        (live_server["data_dir"] / "clubs.json").read_text(encoding="utf-8")
    )["clubs"]
    saved_events = json.loads(
        (live_server["data_dir"] / "competitions.json").read_text(encoding="utf-8")
    )["competitions"]
    assert saved_clubs[0]["points"] == "18"
    assert saved_events[0]["numberOfPlaces"] == "8"


def test_browser_creates_and_confirms_future_event(browser, live_server):
    browser.get(f"{live_server['url']}/competitions/new")
    browser.find_element(By.ID, "name").send_keys("Coupe Selenium")
    event_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%dT%H:%M")
    date_input = browser.find_element(By.ID, "date")
    browser.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        date_input,
        event_date,
    )
    assert date_input.get_attribute("value") == event_date
    browser.find_element(By.ID, "places").send_keys("30")
    browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    message = WebDriverWait(browser, 10).until(
        conditions.visibility_of_element_located((By.CLASS_NAME, "messages"))
    )
    saved_events = json.loads(
        (live_server["data_dir"] / "competitions.json").read_text(encoding="utf-8")
    )["competitions"]
    assert "Événement ajouté avec succès" in message.text
    assert any(item["name"] == "Coupe Selenium" for item in saved_events)
