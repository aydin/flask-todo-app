import os
import unittest
import json
from db import db

basedir = os.path.abspath(os.path.dirname(__file__))


class TodoTestCase(unittest.TestCase):
    """This class represents the Todo test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        os.environ['FLASK_ENV'] = 'testing'
        import todo
        self.app = todo.app
        self.db = db
        self.client = self.app.test_client()
        self.todo_item = {'name': 'test todo item'}

        # binds the app to the current context
        with self.app.app_context():
            # drop all tables if exists
            self.db.drop_all()
            # create all tables
            self.db.create_all()
        # register a user and get access_token
        test_username = 'main_test_username'
        test_password = 'main_test_password'
        self.register(test_username, test_password)
        resp = self.login(test_username, test_password)
        json_resp = json.loads(resp.data)
        self.access_token = json_resp['access_token']
        self.refresh_token = json_resp['refresh_token']
        # set access_token for all requests
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer %s' % \
                                                         self.access_token

    def register(self, username, password):
        return self.client.post('/registration', data=dict(
            username=username,
            password=password
        ))

    def login(self, username, password):
        return self.client.post('/login', data=dict(
                    username=username,
                    password=password
                ))

    def logout_access(self):
        return self.client.post('/logout/access')

    def logout_refresh(self):
        return self.client.post('/logout/refresh')

    def test_register_success(self):
        resp = self.register('test', 'test')
        self.assertEqual(resp.status_code, 201)
        json_resp = json.loads(resp.data)
        self.assertEqual('User test is created', json_resp['message'])

    def test_create_todo(self):
        """Test API can create a todo (POST request)"""
        resp = self.client.post('/todos', data=self.todo_item)
        self.assertEqual(resp.status_code, 201)
        json_resp = json.loads(resp.data)
        self.assertEqual('test todo item', json_resp['name'])

    def test_get_all_todos(self):
        """Test API can get a todo (GET request)."""
        todo_item_2 = {'name': 'test todo item 2'}
        self.client.post('/todos', data=self.todo_item)
        self.client.post('/todos', data=todo_item_2)
        resp = self.client.get('/todos')
        self.assertEqual(resp.status_code, 200)
        json_resp = json.loads(resp.data)
        self.assertEqual(2, len(json_resp))
        for k in json_resp:
            self.assertIn(k['name'], (self.todo_item['name'],
                                      todo_item_2['name']))

    def test_get_todo_by_id(self):
        """Test API can get a single todo by using it's id."""
        resp = self.client.post('/todos', data=self.todo_item)
        todo_id = json.loads(resp.data)['id']

        resp = self.client.get('/todos/%s' % todo_id)
        json_result = json.loads(resp.data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.todo_item['name'], json_result['name'])

    def test_update_todo(self):
        """Test update todo item. (PUT request)"""
        resp = self.client.post('/todos', data=self.todo_item)
        todo_id = json.loads(resp.data)['id']
        updated_name = "Updated todo name"

        resp = self.client.put('/todos/%s' % todo_id,
                               data={"name": updated_name})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/todos/%s' % todo_id)
        json_resp = json.loads(resp.data)
        self.assertEqual(updated_name, json_resp['name'])

    def test_delete_todo(self):
        """Test delete todo item. (DELETE request)."""
        resp = self.client.post('/todos', data=self.todo_item)
        todo_id = json.loads(resp.data)['id']

        resp = self.client.delete('/todos/%s' % todo_id)
        self.assertEqual(resp.status_code, 204)
        # Test to see if it exists, should return a 404
        resp = self.client.get('/todos/%s' % todo_id)
        self.assertEqual(resp.status_code, 404)

    def test_another_users_todo_access(self):
        # create todo object with main_test_username
        resp = self.client.post('/todos', data=self.todo_item)
        todo_id = json.loads(resp.data)['id']
        # register another user
        resp = self.register('another_test_user', 'another_test_password')
        second_access_token = json.loads(resp.data)['access_token']
        # set client header new access_token
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer %s' % \
                                                         second_access_token
        # try to get created todo object with different user token
        resp = self.client.get('/todos/%s' % todo_id)
        self.assertEqual(resp.status_code, 404)
        # set old user access_token and confirm object is accessible
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer %s' % \
                                                         self.access_token
        resp = self.client.get('/todos/%s' % todo_id)
        self.assertEqual(resp.status_code, 200)

    def test_user_logout_access_token(self):
        # create todo object with self.access_token
        resp = self.client.post('/todos', data=self.todo_item)
        self.assertEqual(resp.status_code, 201)
        # logout access_token
        self.logout_access()
        # try to create todo object with logged out access_token
        resp = self.client.post('/todos', data=self.todo_item)
        self.assertEqual(resp.status_code, 401)
        json_resp = json.loads(resp.data)
        self.assertEqual('Token has been revoked', json_resp['msg'])

    def test_user_logout_refresh_token(self):
        # set current token as refresh token
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer %s' % \
                                                         self.refresh_token
        # refresh access_token with working refresh_token
        resp = self.client.post('/token/refresh')
        self.assertEqual(resp.status_code, 200)
        # logout refresh_token
        self.logout_refresh()
        # try to refresh access_token logged out refresh_token
        resp = self.client.post('/token/refresh')
        self.assertEqual(resp.status_code, 401)
        json_resp = json.loads(resp.data)
        self.assertEqual('Token has been revoked', json_resp['msg'])

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            self.db.session.remove()
            self.db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
