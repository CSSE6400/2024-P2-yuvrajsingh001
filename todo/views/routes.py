from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    completed = request.args.get('completed')
    window = request.args.get('window')

    # Query all todos
    todos_query = Todo.query

    # Apply filtering based on completion status
    if completed is not None:
        completed_bool = bool(completed.lower() == 'true')
        todos_query = todos_query.filter_by(completed=completed_bool)
        
    if window is not None:
        window_date = datetime.now() + timedelta(days=int(window))
        todos_query = todos_query.filter(Todo.deadline_at <= window_date)

    # Execute the query
    todos = todos_query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    if not request.is_json:
        return jsonify({'error': 'Invalid JSON request'}), 400
    
    if 'title' not in request.json:
        return jsonify({'error': 'Title is required'}), 400
    
    allowed_fields = ['title', 'description', 'completed', 'deadline_at']
    extra_fields = set(request.json.keys()) - set(allowed_fields)

    if extra_fields:
        return jsonify({'error': f'Extra fields not allowed: {", ".join(extra_fields)}'}), 400
    
    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
        
    # Adds a new record to the database or will update an existing record
    db.session.add(todo)
    
    # Commits the changes to the database, this must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    if not request.is_json:
        return jsonify({'error': 'Invalid JSON request'}), 400

    allowed_fields = ['title', 'description', 'completed', 'deadline_at']
    extra_fields = set(request.json.keys()) - set(allowed_fields)

    if extra_fields:
        return jsonify({'error': f'Extra fields not allowed: {", ".join(extra_fields)}'}), 400
    
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200

 
