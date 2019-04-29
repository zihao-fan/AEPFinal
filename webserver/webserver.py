from flask import Flask, request, Response
import json
import mysql.connector

db = mysql.connector.connect(user='root', 
                password='my-secret-pw', 
                host='127.0.0.1',
                database='demo',
                port=3309,
                auth_plugin='mysql_native_password')
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
    return max(ids) + 1

def convert_to_dict(id, title, is_completed, email):
    return {'id': id, 'title': title, 'is_completed': is_completed, 'email': email}
        
@app.route('/v1/tasks', methods=['POST'])
def add_task():
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
                sql_query = "INSERT INTO tasks (id, task, is_completed) VALUES ({}, '{}', {})".format(id, title, is_completed)
                update_database(sql_query)
                return_data['tasks'].append({'id': id})
            resp = Response(json.dumps(return_data), mimetype='application/json', status=201)
        else:
            title = arguments.get('title')
            is_completed = arguments.get('is_completed')
            id = get_id()
            # new_task = Task(title, is_completed, id)
            # task_data[id] = new_task
            sql_query = "INSERT INTO tasks (id, task, is_completed) VALUES ({}, '{}', {})".format(id, title, is_completed)
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
        resp = Response(json.dumps(convert_to_dict(tasks[0])), status=200)
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
        sql = "UPDATE tasks SET title = '{}', is_completed = '{}' WHERE id = {}".format(title, is_completed, id)
        resp = Response(status=204)
    else:
        resp = Response(json.dumps({'error': "There is no task at that id"}), status=404)
    return resp

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response