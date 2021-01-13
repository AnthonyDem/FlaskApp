from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required, get_jwt_identity
from videoblog.schemas import VideoSchema
from videoblog.models import Video
from videoblog import logger, docs
from flask import Blueprint, jsonify

videos = Blueprint('videos', __name__)


@videos.route('/videos', methods=['GET'])
@jwt_required
@marshal_with(VideoSchema(many=True))
def get_videos():
    try:
        user_id = get_jwt_identity()
        videos = Video.get_video_list(user_id=user_id)
    except Exception as e:
        logger.warning(f'user: {user_id} videos - read action falling with error {e}')
        return {'message': str(e)}, 400
    return videos


@videos.route('/videos', methods=['POST'])
@jwt_required
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def post_video(**kwargs):
    try:
        user_id = get_jwt_identity()
        new_video = Video(user_id=user_id, **kwargs)
        new_video.save()
    except Exception as e:
        logger.warning(f'user: {user_id} video - create action failed with error {e}')
        return {'message': str(e)}, 400
    return new_video


@videos.route('/videos/<int:video_id>/', methods=['PUT'])
@jwt_required
@marshal_with(VideoSchema)
@use_kwargs(VideoSchema)
def update_videos_list(video_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        video = Video.get_video(video_id, user_id)
        video.update(**kwargs)
    except Exception as e:
        logger.warning(f'user: {user_id} video: {video_id} - updated failed with error {e}')
        return {'message': str(e)}, 400
    return video


@videos.route('/videos/<int:video_id>/', methods=['DELETE'])
@jwt_required
@marshal_with(VideoSchema)
def delete_video(video_id):
    try:
        user_id = get_jwt_identity()
        video = Video.get_video(video_id, user_id)
        video.delete()
    except Exception as e:
        logger.warning(f'user: {user_id} video: {video_id} deleting failed with error {e}')
        return {'message': str(e)}, 400
    return '', 204


@videos.errorhandler(422)
def error_handler(err):
    headers = err.data.get('headers', None)
    message = err.data.get('message', ['Invalid request'])
    logger.warning(f'Invalid input params {message}')
    if headers:
        return jsonify({'message': message}), 400, headers
    else:
        return jsonify({'message': message}), 400


docs.register(get_videos, blueprint='videos')
docs.register(post_video, blueprint='videos')
docs.register(update_videos_list, blueprint='videos')
docs.register(delete_video, blueprint='videos')