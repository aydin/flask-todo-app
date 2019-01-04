"""Argument Parser objects"""

from flask_restful import reqparse
from datetime import datetime


def valid_date(value, name):
    """
    Validation function for date input

    Args:
        value(date): date string
        name(str): parameter name(due_date e.g.)
    Returns:
        (datetime): parsed date string
    Raises:
        ValueError: If given date string's format is not correct
    """
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("The parameter '{}' is not valid date(%Y-%m-%d). "
                         "Your input is: {}".format(name, value))


authentication_parser = reqparse.RequestParser()
authentication_parser.add_argument(
    'username', help='username can not be blank', required=True)
authentication_parser.add_argument(
    'password', help='password can not be blank', required=True)

# insert argument parser, name is required field
todo_insert_parser = reqparse.RequestParser()
todo_insert_parser.add_argument(
    'name', help='name can not be blank', required=True
)
todo_insert_parser.add_argument(
    'is_done', help='is_done should be boolean(true/false)', required=False,
    type=bool
)
todo_insert_parser.add_argument(
    'due_date', help='Due date should be %Y-%m-%d formatted', required=False,
    type=valid_date
)

# update argument parser, name is not required
todo_update_parser = reqparse.RequestParser()
todo_update_parser.add_argument(
    'name', help='name should be valid string', required=False
)
todo_update_parser.add_argument(
    'is_done', help='is_done should be boolean(true/false)', required=False,
    type=bool
)
todo_update_parser.add_argument(
    'due_date', help='due_date should be %Y-%m-%d formatted', required=False,
    type=valid_date
)
