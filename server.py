import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip().casefold()
    club = next(
        (club for club in clubs if club['email'].strip().casefold() == email),
        None,
    )

    if club is None:
        flash('Adresse e-mail inconnue. Vérifiez votre adresse et réessayez.')
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=competitions)
@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition),
        None,
    )

    if foundClub is None or foundCompetition is None:
        flash('Club ou compétition introuvable. Veuillez réessayer.')
        return redirect(url_for('index'))

    return render_template(
        'booking.html',
        club=foundClub,
        competition=foundCompetition,
    )

@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get("competition", "")
    club_name = request.form.get("club", "")

    competition = next(
        (c for c in competitions if c["name"] == competition_name),
        None,
    )
    club = next((c for c in clubs if c["name"] == club_name), None)

    if competition is None or club is None:
        flash("Club ou compétition introuvable.")
        return redirect(url_for("index"))

    try:
        places_required = int(request.form.get("places", ""))
        points_available = int(club["points"])
    except (TypeError, ValueError):
        flash("Veuillez entrer un nombre de places valide.")
        return render_template(
            "welcome.html", club=club, competitions=competitions
        )
    if places_required <= 0:
        flash("Please enter a positive number of places.")
        return render_template(
            "welcome.html", club=club, competitions=competitions
        )
    if places_required > points_available:
        flash("Not enough points")
        return render_template(
            "welcome.html", club=club, competitions=competitions
        )
    if places_required > int(competition["numberOfPlaces"]):
        flash("Not enough places")
        return render_template(
            "welcome.html", club=club, competitions=competitions
        )

    competition["numberOfPlaces"] = str(
        int(competition["numberOfPlaces"]) - places_required
    )
    club["points"] = str(points_available - places_required)

    with open("clubs.json", "w") as clubs_file:
        json.dump({"clubs": clubs}, clubs_file, indent=4)

    with open("competitions.json", "w") as competitions_file:
        json.dump({"competitions": competitions}, competitions_file, indent=4)
    flash("Great-booking complete!")
    return render_template(
        "welcome.html", club=club, competitions=competitions
    )

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))