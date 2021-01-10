from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

from models import Video

Base.metadata.create_all(bind=engine)


# videos = [{'id': 1, 'video': 'link/112/22', 'description': 'first video 1'},
#           {'id': 2, 'video': 'link/11232/22', 'description': 'second video 2'}]

@app.route('/videos', methods=['GET'])
def get_videos():
    videos = Video.query.all()
    serialized = []
    for video in videos:
        serialized.append({
            'id': Video.id,
            'name': Video.name,
            'description': Video.description
        })
    return jsonify(serialized)


@app.route('/videos', methods=['POST'])
def post_video():
    new_video = Video(**request.json)
    session.add(new_video)
    session.commit()
    serialized = {
        'id': new_video.id,
        'name': new_video.name,
        'description': new_video.description
    }
    return jsonify(serialized)


@app.route('/videos/<int:video_id>/', methods=['PUT'])
def update_video(video_id):
    video = Video.query.filter(Video.id == video_id).first()
    if not video:
        return {'message': 'Error such video doesn\'t exist'}, 400
    data = request.json
    for key, value in data.items():
        setattr(video, key, value)
    session.commit()
    serialized = {
        'id': video.id,
        'name': video.name,
        'description': video.description
    }
    return serialized


@app.route('/videos/<int:video_id>/', methods=['DELETE'])
def delete_video(video_id):
    video = Video.query.filter(Video.id == video_id).first()
    if not video:
        return {'message': 'Error such video doesn\'t exist'}, 400
    session.delete(video)
    session.commit()
    return '', 204


@app.teardown_appcontext
def shutdown_session(exception):
    session.remove()


if __name__ == '__main__':
    app.run(port='8000')
