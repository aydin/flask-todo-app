# Simple Todo App with Flask

This repo demonstrates simple Todo App in Flask with following components:
* Flask SqlAlchemy
* Flask Migrate
* Flask Restful
* Flask Jwt Extended

## Installation

```shell
git clone https://github.com/aydin/flask-todo-app
cd flask-todo-app
pip install -r requirements.txt
export FLASK_APP=todo.py
```
Run the following commands to create your app's database tables and perform the initial migration
```shell
flask db init
flask db migrate
flask db upgrade
```
To run the web application:
```shell
flask run
```
## How run the tests?
```shell
tox
```

## Deployment
```shell
docker-compose up
```