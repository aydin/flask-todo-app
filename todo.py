import os
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from app import create_app_and_register_db, models, resources
from db import db


config_name = os.getenv('FLASK_ENV', 'development')
app = create_app_and_register_db(config_name)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


@jwt.user_loader_callback_loader
def get_user_from_jwt(jwt_user):
    return models.User.find_by_username(jwt_user)


api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.TodoListResource, '/todos', endpoint='todos')
api.add_resource(resources.TodoResource, '/todos/<todo_id>', endpoint='todo')


if __name__ == '__main__':
    app.run()
