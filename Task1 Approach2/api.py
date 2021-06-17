from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import uuid # to generate random public id

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    due_by = db.Column(db.String(), default=datetime.utcnow())
    status = db.Column(db.String(40), nullable=False)

@app.route('/user', methods=['GET'])
def get_all_users():

    users= User.query.all()

    output=[]
    for user in users:
        user_data ={}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users': output})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    name = data['name']
    password = data['password']

    new_user = User(public_id=str(uuid.uuid4()), name=name, password=password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message':'New User Created'})

@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message':'No user found!'})
    user_data =  {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user': user_data})

@app.route('/user/<public_id>', methods=['PUT'])
def update_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    user.admin =True
    db.session.commit()
    return jsonify({'message':'The user has been promoted to admin'})

@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'No user found!'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message':'The user has been deleted!'})

@app.route('/todo', methods=['GET'])
def get_all__todos():
    todos = Todo.query.all()
    output = []
    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['task'] = todo.task
        todo_data['due_by'] = todo.due_by
        todo_data['status'] = todo.status
        output.append(todo_data)
    return jsonify({'todos': output})

@app.route('/todo', methods=['POST'])
def create_todo():
    data = request.get_json()
    new_todo = Todo(task=data['task'], due_by=data['due_by'], status=data['status'])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': 'A new todo created.'})

@app.route('/todo/<todo_id>', methods=['GET'])
def get_one_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo found!'})

    todo_data = {}
    todo_data['id'] = todo.id
    todo_data['task'] = todo.task
    todo_data['due_by'] = todo.due_by
    todo_data['status'] = todo.status

    return jsonify(todo_data)

@app.route('/todo/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo found!'})

    if todo.status == "Not Started":
        todo.status = "In Progress"
        db.session.commit()
        return jsonify({'message':'status is turned to "In Progress" '})

    elif todo.status == "In Progress":
        todo.status = "Finished"
        db.session.commit()
        return jsonify({'message': 'status is turned to "Finished" '})

    else:
        return jsonify({'message': 'status is already "Finished" '})

@app.route('/todo/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'No todo found!'})

    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message':'This todo is deleted!'})


# This function is not working yet
@app.route('/due?due_date=<due_by>', methods=['GET'])
def get_due_tasks(*args):
    # date_obj = datetime.strptime(due_by, '%d/%m/%y')
    val = args
    todos = Todo.query.all()
    tasks = []
    print(val)
    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['task'] = todo.task
        todo_data['due_by'] = todo.due_by
        todo_data['status'] = todo.status
        if todo_data['due_by'] <= val and todo_data['status'] != 'Finished':
            tasks.append(todo_data['task'])
    return jsonify({"tasks": tasks})

@app.route('/overdue', methods=['GET'])
def get_overdue_tasks():
    todos = Todo.query.all()
    today = date.today()
    tasks = []
    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['task'] = todo.task
        todo_data['due_by'] = todo.due_by
        todo_data['status'] = todo.status
        if todo_data['due_by'] <= str(today) and todo_data['status'] != 'Finished':
            tasks.append(todo_data['task'])
    if not tasks:
        return jsonify({'message':'No task is overdue.'})
    return jsonify({'tasks': tasks})

@app.route('/finished', methods=['GET'])
def get_finished_tasks():
    todos = Todo.query.all()
    finished_tasks = []
    for todo in todos:
        todo_data = {}
        todo_data['id'] = todo.id
        todo_data['task'] = todo.task
        todo_data['due_by'] = todo.due_by
        todo_data['status'] = todo.status
        if todo_data['status'] == 'Finished':
            finished_tasks.append(todo_data['task'])
    return jsonify({'Completed tasks': finished_tasks})

if __name__ == "__main__":
    app.run(debug=True)