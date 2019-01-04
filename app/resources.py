import flask_jwt_extended as fjwte
from datetime import datetime
from flask_restful import Resource, fields, marshal_with, abort
from app import parsers
from app.models import User, RevokedTokenModel, Todo


class UserRegistration(Resource):
    """
    User Registration class
    Creates user with given username/password
    Then creates access/refresh token for given user and return all
    """
    def __init__(self):
        self.reqparse = parsers.authentication_parser
        super(UserRegistration, self).__init__()

    def post(self):
        data = self.reqparse.parse_args()
        # if user already exist
        if User.find_by_username(data['username']):
            return {
                'message': 'User %s already exists' % data['username']},\
                   409

        new_user = User(username=data['username'],
                        password=User.generate_password_hash(data['password'])
                        )
        new_user.save()
        access_token = fjwte.create_access_token(identity=data['username'])
        refresh_token = fjwte.create_refresh_token(identity=data['username'])
        return {
            'message': 'User %s is created' % data['username'],
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201


class UserLogin(Resource):
    """
    User Login class
    Authenticate given username/password, if success returns
    access_token and refresh_token for given user
    """
    def __init__(self):
        self.reqparse = parsers.authentication_parser
        super(UserLogin, self).__init__()

    def post(self):
        """
        Logs in user

        Params:
            username(str): username
            password(str): password
        Returns:
            message(str): response message(success/fail)
            access_token(str): access token
            refresh_token(str): refresh token
        """
        data = self.reqparse.parse_args()
        current_user = User.find_by_username(data['username'])

        if not current_user:
            return {
                'message': 'User %s doesn\'t exist' % data['username']}

        if User.verify_password(data['password'], current_user.password):
            access_token = fjwte.create_access_token(identity=data['username'])
            refresh_token = fjwte.create_refresh_token(
                identity=data['username']
            )
            return {
                'message': 'Logged in as %s' % current_user.username,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}, 403


class UserLogoutAccess(Resource):
    """
    User Logout class for access token
    Logs out attached user with given access_token
    Revokes given token
    """
    @fjwte.jwt_required
    def post(self):
        jti = fjwte.get_raw_jwt()['jti']
        revoked_token = RevokedTokenModel(jti=jti)
        revoked_token.save()
        return {'message': 'Access token has been revoked'}


class UserLogoutRefresh(Resource):
    """
    User Logout class for refresh token
    Logs out attached user with given refresh_token
    Revokes given token
    """
    @fjwte.jwt_refresh_token_required
    def post(self):
        jti = fjwte.get_raw_jwt()['jti']
        revoked_token = RevokedTokenModel(jti=jti)
        revoked_token.save()
        return {'message': 'Refresh token has been revoked'}


class TokenRefresh(Resource):
    """
    Creates new access_token for user with given refresh_token
    and returns it
    """
    @fjwte.jwt_refresh_token_required
    def post(self):
        current_user = fjwte.get_jwt_identity()
        access_token = fjwte.create_access_token(identity=current_user)
        return {'access_token': access_token}


todo_fields = {  # marshall object, will be used for all Todo objects
    'id': fields.Integer,
    'name': fields.String,
    'is_done': fields.Boolean,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'due_date': fields.DateTime(dt_format='iso8601'),
    'completed_date': fields.DateTime(dt_format='iso8601'),
}


class TodoResource(Resource):
    """
    Todo Resource class
    Get, Update and Delete operations will be done here
    """

    def __init__(self):
        self.reqparse = parsers.todo_update_parser
        super(TodoResource, self).__init__()

    decorators = [fjwte.jwt_required, marshal_with(todo_fields)]

    @staticmethod
    def get_todo_by_user_id(todo_id):
        """
        Filters given todo id and user id

        Args:
            todo_id(int): todo object id
        Returns:
            object(todo): filtered todo object
        """
        current_user = fjwte.get_current_user()
        todo = Todo.get_item_by_user_id(todo_id, current_user.id)
        if not todo:
            abort(404, message="Todo %s doesn't exist" % todo_id)
        return todo

    def get(self, todo_id):
        """
        Returns given Todo object

        Args:
            todo_id(int): todo object id
        Returns:
            object(todo)
        """
        return self.get_todo_by_user_id(todo_id)

    def delete(self, todo_id):
        """
        Deletes given Todo object

        Args:
            todo_id(int): todo object id
        """
        todo = self.get_todo_by_user_id(todo_id)
        todo.delete()
        return '', 204

    def put(self, todo_id):
        """
        Updates given Todo object

        Args:
            todo_id(int): todo object id
        Params:
            name(str): name
            is_done(bool): it is already done or not
            due_date(date): due date of todo

        Returns:
            object(todo)
        """
        todo = self.get_todo_by_user_id(todo_id)
        data = self.reqparse.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(todo, key, value)
        # if is_done True set completed_date as now
        if data.get('is_done'):
            todo.completed_date = datetime.utcnow()
        todo.save()
        return todo, 200


class TodoListResource(Resource):
    decorators = [fjwte.jwt_required, marshal_with(todo_fields)]

    def __init__(self):
        self.reqparse = parsers.todo_insert_parser
        super(TodoListResource, self).__init__()

    def get(self):
        """
        Returns given user's Todo objects

        Returns:
            objects(list): Todo objects list
        """
        current_user = fjwte.get_current_user()
        return Todo.get_items_by_user_id(current_user.id)

    def post(self):
        """
        Creates Todo object

        Params:
            name(str): name
            is_done(bool): it is already done or not
            due_date(date): due date of todo
        Returns:
            object(todo)
        """
        data = self.reqparse.parse_args()
        new_todo = Todo(name=data['name'], user_id=fjwte.get_current_user().id)
        for key, value in data.items():
            if value is not None:
                setattr(new_todo, key, value)
        # if is_done True set completed_date as now
        if data.get('is_done'):
            new_todo.completed_date = datetime.utcnow()
        new_todo.save()
        return new_todo, 201
