import os
import unittest
import requests
import time

class FlaskrTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        time.sleep(2)
        url = 'http://127.0.0.1:5000/v1/tasks/remove'
        response = requests.get(url)

    def test_0_connect_db(self):
        url = 'http://127.0.0.1:5000/v1/tasks'
        response = requests.get(url)
        assert response.status_code == 200

    def test_1_remove_all(self):
        url = 'http://127.0.0.1:5000/v1/tasks/remove'
        response = requests.get(url)
        assert response.status_code == 200

    def test_2_insert_in_db(self):
        headers = {"Content-Type": "application/json"}
        url = 'http://127.0.0.1:5000/v1/tasks'

        data = {"title": "Test Task 1", "is_completed": "true"}
        response = requests.post(url, json=data, headers=headers)

        data = {"title": "Test Task 2", "is_completed": "false"}
        response = requests.post(url, json=data, headers=headers)

        response = requests.get(url)
        tasks = response.json()['tasks']
        assert response.status_code==200

    def test_3_bulk_insert(self):
        headers = {"Content-Type": "application/json"}
        url = 'http://127.0.0.1:5000/v1/tasks'
        data = {"tasks": [{"title": "Test Task 3", "is_completed": "true"}, 
            {"title": "Test Task 4", "is_completed": "false"}]}
        response = requests.post(url, json=data, headers=headers)
        response = requests.get(url)
        tasks = response.json()['tasks']
        assert response.status_code==200

    def test_4_getting_a_task(self):
        url = 'http://127.0.0.1:5000/v1/tasks/1'
        response = requests.get(url)
        tasks = response.json()
        assert tasks['id'] == 1

    def test_5_getting_a_invalid_task(self):
        url = 'http://127.0.0.1:5000/v1/tasks/17'
        response = requests.get(url)
        error = response.json()
        assert "error" in error

    def test_6_delete_existing_task(self):
        url = 'http://127.0.0.1:5000/v1/tasks/1'
        response = requests.delete(url)
        assert response.status_code == 204

    # def test_7_delete_nonexsiting_task(self):
    #     url = 'http://127.0.0.1:5000/v1/tasks/17'
    #     response = requests.delete(url)
    #     assert response.status_code == 204

    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == '__main__':
    unittest.main()