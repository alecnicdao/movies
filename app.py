

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from flask_sqlalchemy import SQLAlchemy



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


@app.route("/")
def index():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/admin")
@app.route("/admin/movies")
@login_required
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
