from functools import wraps

from flask import ( Flask, render_template, request, redirect, url_for, flash, g, session)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}/{}".format(
    app.root_path, "movies.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "b2de7FkqvkMyqzNFzxCkgnPKIGP6i4"

db = SQLAlchemy(app)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False)
    genre = db.relationship("Genre", backref=db.backref("Movie", lazy=True))
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"), nullable=False)
    director = db.relationship("Director", backref=db.backref("Movie", lazy=True))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def check_password(self, value):
        return check_password_hash(self.password, value)

db.create_all()

@app.before_request
def load_user():
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id is not None else None

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)

    return decorated_function

@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        user = User.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not user.check_password(password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id 
            return redirect(url_for("movies"))

        flash(error)

    return render_template("admin/login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/register")
def register():
    user = User(username="admin", password=generate_password_hash("admin4book"))
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("index"))

@app.route("/")
def index():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/admin")
@app.route("/admin/movies")
def movies():
    movies = Movie.query.all()
    return render_template("admin/movies.html", movies=movies)


@app.route("/admin/create/movie", methods=("GET", "POST"))
@login_required
def create_movie():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        director_id = request.form["director_id"]
        genre_id = request.form["genre_id"]

        error = None

        if not name:
            error = "Name is required."

        if error is None:
            movie = Movie(
                name=name,
                description=description,
                director_id=director_id,
                genre_id=genre_id,
            )
            db.session.add(movie)
            db.session.commit()

            return redirect(url_for("movies"))

        flash(error)

    directors = Director.query.all()
    genres = Genre.query.all()
    return render_template("admin/movie_form.html", directors=directors, genres=genres)


@app.route("/admin/edit/movie/<id>", methods=("GET", "POST"))
@login_required
def edit_movie(id):
    movie = Movie.query.get_or_404(id)

    if request.method == "POST":
        movie.name = request.form["name"]
        movie.description = request.form["description"]
        movie.director_id = request.form["director_id"]
        movie.genre_id = request.form["genre_id"]

        error = None

        if not request.form["name"]:
            error = "Name is required."

        if error is None:
            db.session.commit()

            return redirect(url_for("movies"))

        flash(error)

    directors = Director.query.all()
    genres = Genre.query.all()
    return render_template(
        "admin/movie_form.html",
        name=movie.name,
        description=movie.description,
        directors=directors,
        director_id=movie.director_id,
        genres=genres,
        genre_id=movie.genre_id,
    )


@app.route("/admin/delete/movie/<id>")
@login_required
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()

    return redirect(url_for("movies"))


@app.route("/admin/create/genre", methods=("GET", "POST"))
@login_required
def create_genre():
    if request.method == "POST":
        name = request.form["name"]

        error = None

        if not name:
            error = "Name is required."

        if error is None:
            genre = Genre(name=name)
            db.session.add(genre)
            db.session.commit()

            return redirect(url_for("movies"))

        flash(error)

    return render_template("admin/genre_form.html")


@app.route("/admin/create/director", methods=("GET", "POST"))
@login_required
def create_director():
    if request.method == "POST":
        name = request.form["name"]

        error = None

        if not name:
            error = "Name is required."

        if error is None:
            director = Director(name=name)
            db.session.add(director)
            db.session.commit()

            return redirect(url_for("movies"))

        flash(error)

    return render_template("admin/director_form.html")

@app.route('/browse/')
@login_required
def browse():
    return render_template('browse.html')

@app.route('/genre/<category>')
def category(category):
    cat = content['category'][category]
    return render_template('category.html', genre=cat['genre'], genreDesc=cat['genreDesc'], movies=cat['movies'])

@app.route('/movies/<movie>')
def movie(movie):
    theMovie = content['movie'][movie]
    if 'subtitle' in theMovie:
        return render_template('movie.html', title=theMovie['title'], subtitle=theMovie['subtitle'], director=theMovie['director'], description=theMovie['description'])
    else:
        return render_template('movie.html', title=theMovie['title'], director=theMovie['director'], description=theMovie['description'])


content = {
    'category': {
        'action': {
            'genre': 'Action',
            'genreDesc': 'Action film is a film genre in which the protagonist or protagonists are thrust into a series of events that typically include violence, extended fighting, physical feats, rescues and frantic chases.',
            'movies': [
                { 'title': 'Black Panther', 'route': 'black-panther' },
                { 'title': 'Thor Ragnarok', 'route': 'thor' },
                { 'title': 'Captain America: Civil War', 'route': 'captain-america' }
            ]
        },
        'adventure': {
            'genre': 'Adventure',
            'genreDesc': 'Adventure films are a genre of film whose plots feature elements of travel.',
            'movies': [
                { 'title': 'Guardians of the Galaxy vol. 2', 'route': 'guardians' },
                { 'title': 'Doctor Strange', 'route': 'doctor' },
                { 'title': 'Captain Marvel', 'route': 'cap-marvel' }
            ]
        },
        'fantasy': {
            'genre': 'Fantasy',
            'genreDesc': 'Fantasy films are films that belong to the fantasy genre with fantastic themes, usually magic, supernatural events, mythology, folklore, or exotic fantasy worlds.',
            'movies': [
                { 'title': 'The Avengers', 'route': 'avengers' },
                { 'title': 'Avengers: Infinity War', 'route': 'war' },
                { 'title': 'Avengers: Endgame', 'route': 'endgame' }
            ]
        }
    },
    'movie': {
        'black-panther': {
            'title': 'The Black Panther',
            'subtitle': 'Action/Adventure',
            'director': 'Ryan Coogler',
            'description': 'After the death of his father, TChalla returns home to the African nation of Wakanda to take his rightful place as king.'
        },
        'thor': {
            'title': 'Thor Ragnarok',
            'subtitle': 'Action/Adventure',
            'director': 'Taika Waititi',
            'description': 'Imprisoned on the other side of the universe, the mighty Thor finds himself in a deadly gladiatorial contest that pits him against the Hulk, his former ally and fellow Avenger.'
        },
        'captain-america': {
            'title': 'Captain America: Civil War',
            'subtitle': 'Action/Adventure',
            'director': 'Joe Russo, Anthony Russo',
            'description': 'Political pressure mounts to install a system of accountability when the actions of the Avengers lead to collateral damage.'
        },
        'guardians': {
            'title': 'Guardians of the Galaxy vol. 2',
            'subtitle': 'Action/Scifi/Adventure',
            'director': 'James Gunn',
            'description': 'Peter Quill and his fellow Guardians are hired by a powerful alien race, the Sovereign, to protect their precious batteries from invaders.'
        },
        'doctor': {
            'title': 'Doctor Strange',
            'subtitle': 'Action/Fantasy/Adventure',
            'director': 'Scott Derrickson',
            'description': 'Dr. Stephen Strange\'s (Benedict Cumberbatch) life changes after a car accident robs him of the use of his hands.'
        },
        'cap-marvel': {
            'title': 'Captain Marvel',
            'subtitle': 'Action/Scifi/Adventure',
            'director': 'Anna Boden, Ryan Fleck',
            'description': 'Captain Marvel is an extraterrestrial Kree warrior who finds herself caught in the middle of an intergalactic battle between her people and the Skrulls.'
        },
        'avengers': {
            'title': 'The Avengers',
            'subtitle': 'Action/Scifi/Fantasy',
            'director': 'Joss Whedon, Joe Russo, Anthony Russo',
            'description': 'Marvel\'s The Avengers, also known as The Avengers and Avengers Assemble, is a 2012 superhero film, based on the Marvel Comics superhero team of the same name. The film is a crossover/sequel to Iron Man, The Incredible Hulk, Iron Man 2, Thor, and Captain America: The First Avenger.'
        },
        'war': {
            'title': 'Avengers: Infinity War',
            'subtitle': 'Action/Scifi/Fantasy',
            'director': 'Joe Russo, Anthony Russo',
            'description': 'Iron Man, Thor, the Hulk and the rest of the Avengers unite to battle their most powerful enemy yet -- the evil Thanos.'
        },
        'endgame': {
            'title': 'Avengers: Endgame',
            'subtitle': 'Action/Scifi/Fantasy',
            'director': 'Joe Russo, Anthony Russo',
            'description': 'Adrift in space with no food or water, Tony Stark sends a message to Pepper Potts as his oxygen supply starts to dwindle.'
        }
    }
}
