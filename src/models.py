import os
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
database_path = os.environ.get("DATABASE_PATH", "postgresql://localhost:5432/capstone")


def setup_db(app, db_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


class MovieCasting(db.Model):
    __tablename__ = "castings"
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'))
    actor_id = db.Column(db.Integer, db.ForeignKey('actors.id', ondelete='CASCADE'))
    actor = db.relationship('Actor', back_populates='movies')
    movie = db.relationship('Movie', back_populates='actors')

    def insert(self):
        db.session.add(self)
        db.session.commit()


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime)
    actors = db.relationship('MovieCasting', back_populates='movie')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # noinspection PyMethodMayBeStatic
    def update(self):
        db.session.commit()

    @property
    def format(self):
        cast = []
        if len(self.actors):
            cast = [
                {
                    'name': cast.actor.name,
                    'age': cast.actor.age
                } for cast in self.actors if cast.actor]
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date,
            'cast': cast
        }


class Actor(db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    gender = db.Column(db.String)
    movies = db.relationship('MovieCasting', back_populates='actor')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # noinspection PyMethodMayBeStatic
    def update(self):
        db.session.commit()

    @property
    def format(self):
        movies = []
        if len(self.movies):
            movies = [
                {
                    'title': casting.movie.title,
                    'release_date': casting.movie.release_date
                } for casting in self.movies if casting.movie]
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'movies': movies
        }
