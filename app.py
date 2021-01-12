from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from apispec.ext.marshmallow import  MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import VideoSchema, AuthSchema, UserSchema
from flask_apispec import use_kwargs, marshal_with

app = Flask(__name__)
app.config.from_object(Config)

client = app.test_client()

engine = create_engine('sqlite:///db.sqlite')

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()

docs.init_app(app)

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()],
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

from models import Video, User

Base.metadata.create_all(bind=engine)


@app.route('/videos', methods=['GET'])
@jwt_required
@marshal_with(VideoSchema(many=True))
def get_videos():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id == user_id)
    return videos


@app.route('/videos', methods=['POST'])
@jwt_required
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def post_video(**kwargs):
    user_id = get_jwt_identity()
    new_video = Video(user_id=user_id, **kwargs)
    session.add(new_video)
    session.commit()
    return new_video


@app.route('/videos/<int:video_id>/', methods=['PUT'])
@jwt_required
@marshal_with(VideoSchema)
@use_kwargs(VideoSchema)
def update_video(video_id, **kwargs):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.id == video_id, Video.user_id == user_id).first()
    if not video:
        return {'message': 'Error such video doesn\'t exist'}, 400
    for key, value in kwargs.items():
        setattr(video, key, value)
    session.commit()
    return video


@app.route('/videos/<int:video_id>/', methods=['DELETE'])
@jwt_required
@marshal_with(VideoSchema)
def delete_video(video_id):
    user_id = get_jwt_identity()
    video = Video.query.filter(Video.id == video_id, Video.user_id == user_id).first()
    if not video:
        return {'message': 'Error such video doesn\'t exist'}, 400
    session.delete(video)
    session.commit()
    return '', 204


@app.route('/register', methods=['POST'])
@marshal_with(AuthSchema)
@use_kwargs(UserSchema)
def register(**kwargs):
    user = User(**kwargs)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {'access_token': token}


@app.route('/login', methods=['POST'])
@use_kwargs(UserSchema(only=['email', 'password']))
@marshal_with(AuthSchema)
def login(**kwargs):
    user = User.authenticate(**kwargs)
    token = user.get_token()
    return {'access_token': token}


@app.teardown_appcontext
def shutdown_session(exception):
    session.remove()


docs.register(get_videos)
docs.register(post_video)
docs.register(update_video)
docs.register(delete_video)
docs.register(register)
docs.register(login)

if __name__ == '__main__':
    app.run(port='8000')
