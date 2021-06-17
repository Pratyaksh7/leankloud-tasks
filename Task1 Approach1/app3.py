from flask import Flask, jsonify, request
from flask_restplus import Api, Resource, fields, reqparse, inputs
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import psycopg2
# psycopg2-binary package

app = Flask(__name__)

# POSTGRESQL_URI ="postgres://" # unique key here.
# connection =psycopg2.connect(POSTGRESQL_URI)
# with connection:
#     with connection.cursor() as cursor:
#         cursor.execute("CREATE TABLE todo (id INT, task TEXT, due_by TEXT, status TEXT);")

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    due_by = db.Column(db.Date, default=datetime.utcnow())
    status = db.Column(db.String(40), nullable=False)

    def __repr__(self) -> str:
        return "{0}-{1}".format(self.task, self.status)

api = Api(app, version='1.0', title='Pratyaksh Api', description='A simple basic API')

ns = api.namespace('todos', description='TODO operations')

todoModel = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique Identifier'),
    'task': fields.String(required=True, description='The actual task'),
    'due_by': fields.Date(required=True, description='When the task should be completed'),
    'status': fields.String(required=True, description=' Not started or In progress or Finished')
})


class TodoDAO(object):
    def __init__(self):
        self.counter = 0
        self.todos = []

    def get(self, id):
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} does not exist".format(id))

    def create(self,data):
        todo = data
        todo['id'] = self.counter = self.counter + 1
        # with connection:
        #     with connection.cursor() as cursor:
        #         cursor.execute("INSERT INTO todo VALUES (%d, %s, %s, %s);", (
        #             todo['id'],
        #             todo['task'],
        #             todo['due_by'],
        #             todo['status'],
        #         ))

        self.todos.append(todo)
        return todo

    def update(self,id, data):
        todo = self.get(id)
        todo.update(data)
        return todo

    def delete(self, id):
        todo = self.get(id)
        self.todos.remove(todo)

DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows the list of all todos ( using get() ) and let us to post new todos ( using post() ) '''
    @ns.doc('list todos')
    @ns.marshal_list_with(todoModel)
    def get(self):
        # with connection:
        #     with connection.cursor() as cursor:
        #         cursor.execute("SELECT * FROM todos;")
        #         todos = cursor.fetchall()
        return DAO.todos

    @ns.doc('create_new_todo')
    @ns.expect(todoModel)
    @ns.marshal_with(todoModel)
    def post(self):
        todo = DAO.create(api.payload)
        # db.session.add(todo)
        # db.session.commit()
        return todo


@ns.route('/<int:id>')
class Todo(Resource):
    ''' Show a single todo item and lets you delete them '''
    @ns.doc('get a particular todo')
    @ns.marshal_with(todoModel)
    def get(self, id):
        return DAO.get(id)

    @ns.doc('Delete a particular todo with its id')
    @ns.response(204,"Todo deleted")
    def delete(self, id):
        ''' Delete a task given its identifier '''
        DAO.delete(id)
        return '', 204

    @ns.doc('Updating a todo with a certain id')
    @ns.expect(todoModel)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

parser = reqparse.RequestParser()
parser.add_argument('due_date', type=inputs.date_from_iso8601, required=True)

@ns.route('/due')
class TodosByDate(Resource):

    @ns.expect(parser)
    def get(self):

        try:
            args = parser.parse_args()
            date = args.get('due_date')
            tasks = []
            for todo in DAO.todos:
                if todo['due_by'] <= str(date) and todo['status'] != 'Finished':
                    tasks.append(todo)

            return tasks

        except:
            return {}, 400

@ns.route('/overdue')
class TodosOverDue(Resource):
    def get(self):
        today = date.today()
        tasks = []
        for todo in DAO.todos:
            if todo['due_by'] <= str(today) and todo['status'] != 'Finished':
                tasks.append(todo)

        return tasks

@ns.route('/finished')
class TodosFinished(Resource):
    def get(self):
        finishedTodo = []
        for todo in DAO.todos:
            if todo['status'] == "Finished":
                finishedTodo.append(todo['task'])

        return finishedTodo

if __name__ == '__main__':
    app.run(debug=True)