from marshmallow import validate, Schema, fields


class VideoSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(255)])
    description = fields.String(required=True, validate=[validate.Length(500)])
    message = fields.String(dump_only=True)


class UserSchema(Schema):
    name = fields.String(required=True, validate=[validate.Length(250)])
    email = fields.String(required=True, validate=[validate.Length(200)])
    password = fields.String(required=True, validate=[validate.Length(100)], load_only=True)
    videos = fields.Nested(VideoSchema, many=True, dump_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)