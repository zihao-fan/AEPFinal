echo 'Testing adding tasks'

curl -d '{"title": "Test Task 1", "is_completed": "true"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/v1/tasks
echo '\n'

curl -d '{"title": "Test Task 2", "is_completed": "false"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/v1/tasks
echo '\n'

echo 'Testing all tasks'

curl http://127.0.0.1:5000/v1/tasks
echo '\n'

echo 'Testing getting a task'

curl http://127.0.0.1:5000/v1/tasks/1
echo '\n'

curl http://127.0.0.1:5000/v1/tasks/17
echo '\n'

echo 'Testing removing task'

curl http://127.0.0.1:5000/v1/tasks/1 -X DELETE
echo '\n'

curl http://127.0.0.1:5000/v1/tasks
echo '\n'

echo 'Testing updating task'

curl -d '{"title": "Test Task 1", "is_completed": "false"}' -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/v1/tasks/0
echo '\n'

curl http://127.0.0.1:5000/v1/tasks
echo '\n'

echo 'Testing bulk adding tasks'

curl -d '{"tasks": [{"title": "Test Task 3", "is_completed": "true"}, {"title": "Test Task 4", "is_completed": "false"}] }' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/v1/tasks
echo '\n'

curl http://127.0.0.1:5000/v1/tasks
echo '\n'

echo 'Testing bulk delete tasks'

curl -d '{"tasks": [{"id": "0"}, {"id": "3"}] }' -H "Content-Type: application/json" -X DELETE http://127.0.0.1:5000/v1/tasks
echo '\n'

curl http://127.0.0.1:5000/v1/tasks
echo '\n'