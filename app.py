from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import Video, User

Base.metadata.create_all(bind=engine)


@app.route('/videos', methods=['GET'])
@jwt_required
def get_videos():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id == user_id)
    serialized = []
    for video in videos:
        serialized.append({
            'id': video.id,
            'name': video.name,
            'user_id': video.user_id,
            'description': video.description
        })
    return jsonify(serialized)


@app.route('/videos', methods=['POST'])
@jwt_required
def post_video():
    user_id = get_jwt_identity()
    new_video = Video(user_id=user_id, **request.json)
    session.add(new_video)
    session.commit()
    serialized = {
        'id': new_video.id,
        'name': new_video.name,
        'user_id': new_video.user_id,
        'description': new_video.description
    }
    return jsonify(serialized)


@app.route('/videos/<int:video_id>/', methods=['PUT'])
@jwt_required
def update_video(video_id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.id == video_id, Video.user_id == user_id).first()
    if not video:
        return {'message': 'Error such video doesn\'t exist'}, 400
    data = request.json
    for key, value in data.items():
        setattr(video, key, value)
    session.commit()
    serialized = {
        'id': video.id,
        'name': video.name,
        'user_id': video.user_id,
        'description': video.description
    }
    return serialized


@app.route('/videos/<int:video_id>/', methods=['DELETE'])
@jwt_required
def delete_video(video_id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.id == video_id, Video.user_id == user_id).first()
    if not video:
        return {'message': 'Error such video doesn\'t exist'}, 400
    session.delete(video)
    session.commit()
    return '', 204


@app.route('/register', methods=['POST'])
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/login', methods=['POST'])
def login():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def shutdown_session(exception):
    session.remove()


if __name__ == '__main__':
    app.run(port='8000')
