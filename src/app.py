from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Actor, Movie, MovieCasting
from auth import AuthError, requires_auth


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/actors', methods=['POST'])
    @requires_auth('post:actors')
    def create_actors(payload):
        body = request.get_json()
        kwargs = {}
        try:
            kwargs['name'] = body['name']
            kwargs['age'] = body['age']
            kwargs['gender'] = body['gender']
        except KeyError:
            abort(400)
        try:
            actor = Actor(**kwargs)
            actor.insert()
            return jsonify({
                "success": True,
                "created": actor.id
            })
        except Exception:
            abort(422)

    @app.route('/actors', methods=['GET'])
    @requires_auth('get:actors')
    def get_actors(payload):
        actors = Actor.query.all()
        actors = [actor.format for actor in actors]
        return jsonify({
            "success": True,
            "actors": actors
        })

    @app.route('/actors/<actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def delete_actors(payload, actor_id):
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            actor.delete()
            return jsonify({
                "success": True,
                "deleted": actor_id
            })
        except Exception:
            abort(422)

    @app.route('/actors/<actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def update_actors(payload, actor_id):
        body = request.get_json()
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            if not actor:
                abort(404)
            if body.get('name', None):
                actor.name = body['name']
            if body.get('age', None):
                actor.age = body['age']
            if body.get('gender', None):
                actor.gender = body['gender']
            actor.update()
            return jsonify({
                "success": True,
                "actor": actor.format
            })
        except Exception:
            abort(422)

    @app.route('/movies', methods=['GET'])
    @requires_auth('get:movies')
    def get_movies(payload):
        movies = Movie.query.all()
        movies = [movie.format for movie in movies]
        return jsonify({
            "success": True,
            "movies": movies
        })

    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def create_movies(payload):
        """
        release_date format: 2015-01-12 12:45:00
        """
        body = request.get_json()
        kwargs = {}
        try:
            kwargs['title'] = body['title']
            kwargs['release_date'] = body['release_date']
        except KeyError:
            abort(400)
        try:
            movie = Movie(**kwargs)
            movie.insert()
            return jsonify({
                "success": True,
                "created": movie.id
            })
        except Exception:
            abort(422)

    @app.route('/movies/<movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def delete_movies(payload, movie_id):
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            movie.delete()
            return jsonify({
                "success": True,
                "deleted": movie_id
            })
        except Exception:
            abort(422)

    @app.route('/movies/<movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def update_movies(payload, movie_id):
        body = request.get_json()
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            if not movie:
                abort(400)
            if body.get('title', None):
                movie.title = body['title']
            if body.get('release_date', None):
                movie.release_date = body['release_date']
            movie.update()
            return jsonify({
                "success": True,
                "movie": movie.format
            })
        except Exception:
            abort(422)

    @app.route('/casting', methods=['POST'])
    @requires_auth('post:castings')
    def create_castings(payload):
        body = request.get_json()
        kwargs = {}
        movie = None
        actor = None
        try:
            kwargs['movie_id'] = body['movie_id']
            kwargs['actor_id'] = body['actor_id']
            movie = Movie.query.get(body['movie_id'])
            actor = Actor.query.get(body['actor_id'])
        except KeyError:
            abort(400)
        try:
            casting = MovieCasting(**kwargs)
            casting.insert()
            return jsonify({
                "success": True,
                "movie": movie.title,
                "actor": actor.name
            })
        except Exception:
            abort(422)

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "not found"
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
