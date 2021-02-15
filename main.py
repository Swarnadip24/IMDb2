from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import pymysql
pymysql.install_as_MySQLdb()                             # it removes MySQLdb error


app = Flask(__name__)

app.config['SECRET_KEY'] = 'Hello'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/newdb2'                # connection with Db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    director = db.Column(db.String(50))
    imdb_score = db.Column(db.Integer)
    popularity = db.Column(db.Integer)


def auth_required(f):                                               # http Basic Authentication
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'username' and auth.password == 'password':
            return f(*args, **kwargs)

        return make_response('Please login first..!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated

@app.route('/')
def index_page():
    if request.authorization and request.authorization.username == 'username' and request.authorization.password == 'password':
        return '<h1>You are logged in Now...</h1>'

    return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})


@app.route('/add_movie',methods=['POST'])                                  # route to add movies
@auth_required
def add_movie():
    data = request.get_json()
    new = Movie(name=data['name'],genre=data['genre'],director=data['director'],imdb_score=data['imdb_score'],popularity=data['popularity'])
    db.session.add(new)
    db.session.commit()
    return jsonify({'message':'Movie Added...!'})


@app.route('/update/<name>', methods=['PUT'])                                        # route to update movies
@auth_required
def update_movie(name):
    stu = Movie.query.filter_by(name=name).first()
    db.session.commit()
    return jsonify({'message': 'Movie Updated...!'})


@app.route('/delete/<name>', methods=['DELETE'])                                     # route to delete movies
@auth_required
def delete_movie(name):
    data = Movie.query.filter_by(name=name).first()
    if not data: return jsonify({'message': 'Movies not found...'})                  # Handled exception
    db.session.delete(data)
    db.session.commit()
    return jsonify({'message': 'Movie Deleted...!'})


@app.route('/movies',methods=['GET'])                                 # route to search movies
def movies():
    all_data = Movie.query.all()
    if not all_data: return jsonify({'message':'Movies not found...'})           # Handled exception
    output = []
    for data in all_data:
        dict = {}
        dict['id'] = data.id
        dict['name'] = data.name
        dict['genre'] = data.genre
        dict['director'] = data.director
        dict['imdb_score'] = data.imdb_score
        dict['popularity'] = data.popularity
        output.append(dict)

    return jsonify({'movies_list':output})

'''
@app.route('/movies/<string:name>',methods=['GET'])
def get_one_movie(name):
    all_data = Movie.query.all()
    try:
        data = [movie for movie in all_data if movie['name']==name]
    except:
        return jsonify({'message':'Not found'})
    return jsonify({'list':data[0]})
'''

if __name__ == '__main__':
    db.create_all()                                     # to create database table
    app.run(debug=1)
