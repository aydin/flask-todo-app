from db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class BaseModel:
    """
    Base for all models, providing add, save, delete methods.
    """

    def delete(self):
        """Deletes this model from the db (through db.session)"""
        db.session.delete(self)
        db.session.commit()

    def save(self):
        """Adds this model to the db (through db.session)"""
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def get_items_by_user_id(cls, user_id):
        """
        Filters Todo objects with given user id

        Args:
            cls(Todo): Todo class instance
            user_id(int): logged_in user id
        Returns:
            objects(Todo): Todo objects filtered by user_id
        """
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_item_by_user_id(cls, todo_id, user_id):
        """
        Filters Todo objects with given user id and todo_id

        Args:
            cls(Todo): Todo class instance
            todo_id(int): Todo object id
            user_id(int): logged_in user id
        Returns:
            object(Todo): Todo objects filtered by user_id and todo_id
        """
        return cls.query.filter_by(id=todo_id, user_id=user_id).first()


class User(db.Model, BaseModel):
    """User Model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True,
                         nullable=False)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def generate_password_hash(password):
        """
        Generates sha256 hashed password with given clear text password

        Args:
             password(str): clear text password
        Returns:
            (str): sha256 hashed password
        """
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password, hashed_password):
        """
        Verifies if given hashed & clear text passwords matches

        Args:
             password(str): clear text password
             hashed_password(str): hashed password
        Returns:
            bool: True if passwords matches else False
        """
        return check_password_hash(hashed_password, password)

    @classmethod
    def find_by_username(cls, username):
        """
        Filters User objects with given username

        Args:
             username(str): username
        Returns:
            (User): User object
        """
        return cls.query.filter_by(username=username).first()


class Todo(db.Model, BaseModel):
    """Todo Model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(140))
    is_done = db.Column(db.Boolean, index=True, default=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    due_date = db.Column(db.Date, index=True, nullable=True)
    completed_date = db.Column(db.DateTime, index=True, nullable=True)


class RevokedTokenModel(db.Model, BaseModel):
    """Revoked Token Model"""
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    @classmethod
    def is_jti_blacklisted(cls, jti):
        """
        Checks if given Json token blacklisted

        Args:
            cls(RevokedTokenModel): RevokedTokenModel class instance
            jti(str): json token
        Returns:
            (bool): True if given json token blacklisted else False

        """
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
