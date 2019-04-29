import os
import unittest
import requests
import time

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        time.sleep(2)

    def test_connect_db(self):
        url = 'http://127.0.0.1:5000/v1/tasks'
        response = requests.get(url)
        assert response.status_code == 200

    def test_remove_all(self):
        url = 'http://127.0.0.1:5000/v1/tasks/remove'
        response = requests.get(url)
        assert response.status_code == 200

    def test_insert_in_db(self):
        headers = {"Content-Type": "application/json"}
        url = 'http://127.0.0.1:5000/v1/tasks'

        data = {"title": "Test Task 1", "is_completed": "true"}
        response = requests.post(url, json=data, headers=headers)

        data = {"title": "Test Task 2", "is_completed": "false"}
        response = requests.post(url, json=data, headers=headers)

        response = requests.get(url)
        tasks = response.json()['tasks']
        assert len(tasks) == 2

    def tearDown(self):
        url = 'http://127.0.0.1:5000/v1/tasks/remove'
        response = requests.get(url)

if __name__ == '__main__':
    unittest.main()