# Simple Todo App with Flask

This repo demonstrates simple Todo App in Flask with following components:
* Flask SqlAlchemy
* Flask Migrate
* Flask Restful
* Flask Jwt Extended

## Installation
_(Create virtualenv with python3 and activate it)_
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
Set _SECRET_KEY_ and _JWT_SECRET_KEY_ in Dockerfile
```shell
docker-compose up
```

## Request Examples
* Register
```shell
curl -X POST \
  http://127.0.0.1:5000/registration \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d '{"username":"john","password":"johndoe"}'
```
__Get acess_token from response and use it for next requests in Authorization header.__
* Create Todo item

```shell
curl -X POST \
  http://127.0.0.1:5000/todos \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d '{"name":"todo item 1", "due_date": "2019-02-20"}'
```
* List Todo items
```shell
curl -X GET \
  http://127.0.0.1:5000/todos \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json; charset=utf-8'
```

* Update Todo item
```shell
curl -X PUT \
  http://127.0.0.1:5000/todos/1 \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d '{"name": "updated todo item"}'
```
* Delete Todo item
```shell
curl -X DELETE \
  http://127.0.0.1:5000/todos/2 \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json; charset=utf-8'
```
* Revoke access token
```shell
curl -X POST \
  http://127.0.0.1:5000/logout/access \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_access_token' \
  -H 'Content-Type: application/json; charset=utf-8'
```
* Refresh access token
```shell
curl -X POST \
  http://127.0.0.1:5000//token/refresh \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_refresh_token' \
  -H 'Content-Type: application/json; charset=utf-8'
```
* Revoke refresh token
```shell
curl -X POST \
  http://127.0.0.1:5000/logout/refresh \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer your_refresh_token' \
  -H 'Content-Type: application/json; charset=utf-8'
```
