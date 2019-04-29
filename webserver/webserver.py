from flask import Flask, request, Response
import json
import pymysql
import requests

MAILGUN_DOMAIN_NAME="sandboxa18ee74168f74ceb89587ebb1eaec5df.mailgun.org"
MAILGUN_API_KEY="key-42c26d4ddcb7ca7e238d7740de89ef35"
MY_EMAIL = 'fanzihao.thu@gmail.com'

db = pymysql.connect(user='root', 
                password='my-secret-pw', 
                host='127.0.0.1',
                database='demo',
                port=3309)
app = Flask(__name__, static_url_path="/static")

def read_database(sql):
    global db     
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    print("Data fetched from db:", data)
    return data 

def update_database(sql):
    global db 
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()

task_data = dict()

class Task(object):
    """docstring for Task"""
    def __init__(self, title, is_completed, id):
        self.title = title
        self.is_completed = is_completed
        self.id = id

    def __repr__(self):
        return "Task(title={}, is_completed={}, id={})".format(self.title, 
            self.is_completed, self.id)

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'is_completed': self.is_completed}

def get_id():
    sql_query = 'SELECT id FROM tasks'
    ids = read_database(sql_query)
    ids = [item[0] for item in ids]
    if len(ids):
        return max(ids) + 1
    else:
        return 1

def convert_to_dict(id, title, is_completed, email):
    return {'id': id, 'title': title, 'is_completed': is_completed, 'email': email}

def send_email(id, title, receiver):
    url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
    auth = ('api', MAILGUN_API_KEY)
    data = {
        'from': 'Me <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
        'to': receiver,
        'subject': "Task {} completed".format(id),
        'text': "Your Task #{} {} has been completed".format(id, title),
    }

    response = requests.post(url, auth=auth, data=data)
    print(response.status_code)

@app.route('/v1/tasks', methods=['POST'])
def add_task():
    # print('request.headers', request.headers)
    print('request.get_json', request.get_json())
    if request.headers['Content-Type'] == 'application/json':
        arguments = request.get_json()
        if 'tasks' in arguments:
            task_list = arguments.get('tasks')
            return_data = {'tasks':[]}
            for task in task_list:
                title = task.get('title')
                is_completed = task.get('is_completed')
                id = get_id()
                # new_task = Task(title, is_completed, id)
                # task_data[id] = new_task
                sql_query = "INSERT INTO tasks (id, task, is_completed, notify) VALUES ({}, '{}', {}, '{}')".format(id, title, is_completed, MY_EMAIL)
                update_database(sql_query)
                return_data['tasks'].append({'id': id})
            resp = Response(json.dumps(return_data), mimetype='application/json', status=201)
        else:
            title = arguments.get('title')
            is_completed = arguments.get('is_completed')
            id = get_id()
            # new_task = Task(title, is_completed, id)
            # task_data[id] = new_task
            sql_query = "INSERT INTO tasks (id, task, is_completed, notify) VALUES ({}, '{}', {}, '{}')".format(id, title, is_completed, MY_EMAIL)
            update_database(sql_query)
            resp = Response(json.dumps({'id': id}), mimetype='application/json', status=201)
        return resp

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    sql_query = "SELECT * FROM tasks"
    tasks_got = read_database(sql_query)
    # data = {'tasks': [value.to_dict() for key, value in task_data.items()]}
    data = {'tasks': [convert_to_dict(id, title, is_completed, email) for id, title, is_completed, email in tasks_got]}
    resp = Response(json.dumps(data), mimetype='application/json', status=200)
    return resp

@app.route('/v1/tasks/<id>', methods=['GET'])
def get_task(id):
    sql_query = "SELECT * FROM tasks WHERE tasks.id = {}".format(id)
    tasks = read_database(sql_query)
    if len(tasks):
        print(tasks[0])
        resp = Response(json.dumps(convert_to_dict(*tasks[0])), status=200)
    else:
        resp = Response(json.dumps({'error': "There is no task at that id"}), status=404)
    return resp

@app.route('/v1/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    sql_query = "SELECT * FROM tasks WHERE tasks.id = {}".format(id)
    tasks_got = read_database(sql_query)
    if len(tasks_got):
        sql_query = "DELETE FROM tasks WHERE tasks.id = {}".format(id)
        update_database(sql_query)
    return Response(status=204)

@app.route('/v1/tasks', methods=['DELETE'])
def delete_list_of_tasks():
    if request.headers['Content-Type'] == 'application/json':
        arguments = request.get_json()
        task_list = arguments.get('tasks')
        for task in task_list:
            id = str(task['id'])
            sql_query = "SELECT * FROM tasks WHERE tasks.id = {}".format(id)
            tasks_got = read_database(sql_query)
            if len(tasks_got):
                sql_query = "DELETE FROM tasks WHERE tasks.id = {}".format(id)
                update_database(sql_query)
        return Response(status=204)

@app.route('/v1/tasks/<id>', methods=['PUT'])
def edit_task(id):
    sql_query = "SELECT * FROM tasks WHERE tasks.id = {}".format(id)
    tasks = read_database(sql_query)
    if len(tasks):
        arguments = request.get_json()
        title = arguments.get('title')
        is_completed = arguments.get('is_completed')
        if is_completed:
            send_email(id, title, MY_EMAIL)
        sql = "UPDATE tasks SET title = '{}', is_completed = '{}' WHERE id = {}".format(title, is_completed, id)
        resp = Response(status=204)
    else:
        resp = Response(json.dumps({'error': "There is no task at that id"}), status=404)
    return resp

@app.route('/v1/tasks/remove', methods=['GET'])
def remove_all_rows():
    sql_query = 'DELETE FROM tasks'
    update_database(sql_query)
    resp = Response(status=200)
    return resp 

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response