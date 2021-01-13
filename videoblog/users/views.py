from flask_apispec import marshal_with, use_kwargs

from videoblog.schemas import AuthSchema, UserSchema
from videoblog import logger, session, docs
from videoblog.models import User
from flask import Blueprint, jsonify

users = Blueprint('users', __name__)


@users.route('/register', methods=['POST'])
@marshal_with(AuthSchema)
@use_kwargs(UserSchema)
def register(**kwargs):
    try:
        user = User(**kwargs)
        session.add(user)
        session.commit()
        token = user.get_token()
    except Exception as e:
        return {'message': str(e)}, 400
    return {'access_token': token}


@users.route('/login', methods=['POST'])
@use_kwargs(UserSchema(only=['email', 'password']))
@marshal_with(AuthSchema)
def login(**kwargs):
    try:
        user = User.authenticate(**kwargs)
        token = user.get_token()
    except Exception as e:
        return {'message': str(e)}, 400
    return {'access_token': token}


@users.errorhandler(422)
def error_handler(err):
    headers = err.data.get('headers', None)
    message = err.data.get('message', ['Invalid request'])
    logger.warning(f'Invalid input params {message}')
    if headers:
        return jsonify({'message': message}), 400, headers
    else:
        return jsonify({'message': message}), 400


docs.register(register, blueprint='users')
docs.register(login, blueprint='users')