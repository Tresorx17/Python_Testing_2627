import json
import os
import tempfile
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__)
DATA_DIR = os.environ.get("GUDLFT_DATA_DIR", app.root_path)
app.secret_key = "something_special"


def loadClubs():
    with open(os.path.join(DATA_DIR, "clubs.json"), encoding="utf-8") as clubs_file:
        return json.load(clubs_file)["clubs"]


def loadCompetitions():
    with open(
        os.path.join(DATA_DIR, "competitions.json"), encoding="utf-8"
    ) as competitions_file:
        return json.load(competitions_file)["competitions"]


def competitionDate(competition):
    return datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")


def competitionHasPassed(competition):
    try:
        return competitionDate(competition) < datetime.now()
    except (KeyError, TypeError, ValueError):
        return True


def splitCompetitions(items=None):
    items = competitions if items is None else items
    upcoming = [item for item in items if not competitionHasPassed(item)]
    past = [item for item in items if competitionHasPassed(item)]
    # A malformed date is already classified as past; keep sorting robust too.
    def safe_date(item):
        try:
            return competitionDate(item)
        except (KeyError, TypeError, ValueError):
            return datetime.min

    upcoming.sort(key=safe_date)
    past.sort(key=safe_date, reverse=True)
    return upcoming, past


def renderSummary(club):
    upcoming, past = splitCompetitions()
    return render_template(
        "welcome.html",
        club=club,
        upcoming_competitions=upcoming,
        past_competitions=past,
    )


def saveJsonAtomically(path, data):
    directory = os.path.dirname(path)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=directory, delete=False
        ) as temporary_file:
            json.dump(data, temporary_file, indent=4)
            temporary_path = temporary_file.name
        os.replace(temporary_path, path)
    except OSError:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise


clubs = loadClubs()
competitions = loadCompetitions()
app.jinja_env.globals["competition_has_passed"] = competitionHasPassed


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    email = request.form.get("email", "").strip().casefold()
    club = next(
        (
            item
            for item in clubs
            if item["email"].strip().casefold() == email
        ),
        None,
    )
    if club is None:
        flash("Adresse e-mail inconnue. Vérifiez votre adresse et réessayez.")
        return redirect(url_for("index"))
    return renderSummary(club)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    found_club = next((item for item in clubs if item["name"] == club), None)
    found_competition = next(
        (item for item in competitions if item["name"] == competition), None
    )
    if found_club is None or found_competition is None:
        flash("Club ou compétition introuvable. Veuillez réessayer.")
        return redirect(url_for("index"))
    if competitionHasPassed(found_competition):
        flash("Désolé, cet événement est passé. Vous pouvez réserver une autre compétition.")
        return renderSummary(found_club)
    return render_template(
        "booking.html", club=found_club, competition=found_competition
    )


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition_name = request.form.get("competition", "")
    club_name = request.form.get("club", "")
    competition = next(
        (item for item in competitions if item["name"] == competition_name),
        None,
    )
    club = next((item for item in clubs if item["name"] == club_name), None)
    if competition is None or club is None:
        flash("Club ou compétition introuvable.")
        return redirect(url_for("index"))
    if competitionHasPassed(competition):
        flash("Désolé, cet événement est passé. Vous pouvez réserver une autre compétition.")
        return renderSummary(club)

    try:
        places_required = int(request.form.get("places", ""))
        points_available = int(club["points"])
        places_available = int(competition["numberOfPlaces"])
    except (TypeError, ValueError):
        flash("Veuillez entrer des données de réservation valides.")
        return renderSummary(club)

    if places_required <= 0:
        flash("Veuillez saisir un nombre de places supérieur à zéro.")
        return renderSummary(club)
    if places_required > 12:
        flash("Vous pouvez réserver au maximum 12 places.")
        return renderSummary(club)
    if places_required > points_available:
        flash("Points insuffisants.")
        return renderSummary(club)
    if places_required > places_available:
        flash("Nombre de places insuffisant.")
        return renderSummary(club)

    club["points"] = str(points_available - places_required)
    competition["numberOfPlaces"] = str(places_available - places_required)
    try:
        with open(os.path.join(DATA_DIR, "clubs.json"), "w", encoding="utf-8") as clubs_file:
            json.dump({"clubs": clubs}, clubs_file, indent=4)
        with open(
            os.path.join(DATA_DIR, "competitions.json"), "w", encoding="utf-8"
        ) as competitions_file:
            json.dump({"competitions": competitions}, competitions_file, indent=4)
    except OSError:
        club["points"] = str(points_available)
        competition["numberOfPlaces"] = str(places_available)
        flash("La réservation n’a pas pu être enregistrée. Veuillez réessayer.")
        return renderSummary(club)

    flash("Réservation confirmée.")
    return renderSummary(club)


@app.route("/competitions/new", methods=["GET", "POST"])
def addCompetition():
    if request.method == "GET":
        return render_template("new_competition.html")

    name = request.form.get("name", "").strip()
    date_text = request.form.get("date", "").strip()
    places_text = request.form.get("places", "").strip()
    if not name:
        flash("Le nom de l’événement est obligatoire.")
        return render_template("new_competition.html")
    if any(item["name"].casefold() == name.casefold() for item in competitions):
        flash("Un événement porte déjà ce nom.")
        return render_template("new_competition.html")
    try:
        event_date = datetime.strptime(date_text, "%Y-%m-%dT%H:%M")
        places = int(places_text)
    except (TypeError, ValueError):
        flash("Saisissez une date et un nombre de places valides.")
        return render_template("new_competition.html")
    if event_date <= datetime.now():
        flash("La date de l’événement doit être dans le futur.")
        return render_template("new_competition.html")
    if places <= 0:
        flash("Le nombre de places doit être supérieur à zéro.")
        return render_template("new_competition.html")

    new_competition = {
        "name": name,
        "date": event_date.strftime("%Y-%m-%d %H:%M:%S"),
        "numberOfPlaces": str(places),
    }
    updated_competitions = competitions + [new_competition]
    try:
        saveJsonAtomically(
            os.path.join(DATA_DIR, "competitions.json"),
            {"competitions": updated_competitions},
        )
    except OSError:
        flash("L’événement n’a pas pu être enregistré. Réessayez.")
        return render_template("new_competition.html")
    competitions.append(new_competition)
    flash("Événement ajouté avec succès.")
    return render_template("new_competition.html")


@app.route("/leaderboard")
def leaderboard():
    ranked_clubs = sorted(
        clubs, key=lambda club: int(club["points"]), reverse=True
    )
    return render_template("leaderboard.html", clubs=ranked_clubs)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
