from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "" # your tmdb api_key
API_ENDPOINT = "https://api.themoviedb.org/3"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)


# db.create_all() - use this command only on the first time you run the code to create the database


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by("rating").all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie_selected = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_id = request.args.get("id")
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie_selected)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["POST", "GET"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        movie_title = request.form["title"]
        parameters = {"api_key": API_KEY, "query": movie_title}
        response = requests.get(f"{API_ENDPOINT}/search/movie", params=parameters).json()
        all_movies = [{"id": movies["id"], "title": movies["title"], "release_date": movies["release_date"]} for movies in response["results"]]
        return render_template("select.html", all_movies=all_movies)
    return render_template("add.html", form=form)


@app.route("/find")
def find():
    movie_id = request.args.get("id")
    if movie_id:
        parameters = {"api_key": API_KEY}
        response = requests.get(f"{API_ENDPOINT}/movie/{movie_id}", params=parameters).json()
        new_movie_title = response["title"]
        new_movie_year = int(response["release_date"][0:4])
        new_movie_description = response["overview"]
        new_movie_img_url = f"https://image.tmdb.org/t/p/w500{response['poster_path']}"
        new_movie = Movie(title=new_movie_title, year=new_movie_year, description=new_movie_description, img_url=new_movie_img_url)
        db.session.add(new_movie)
        db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
