import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from models import db, Task, User
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/dbft24"
db.init_app(app)
jwt = JWTManager(app)
CORS(app)


@app.route('/token/<email>', methods=['GET'])
def token(email):

    data = {
        "access_token": create_access_token(identity=email)
    }

    return jsonify(data), 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email:
        return jsonify({ "message": "Email is required"}), 400
    
    if not password:
        return jsonify({ "message": "Password is required"}), 400
    
    userFound = User.query.filter_by(email=email).first()

    if not userFound:
        return jsonify({ "message": "email/password are incorrects"}), 401
    
    if not check_password_hash(userFound.password, password):
        return jsonify({ "message": "email/password are incorrects"}), 401
    
    access_token = create_access_token(identity=userFound.id)
    datos = {
        "access_token": access_token,
        "user": userFound.serialize()
    }
    return jsonify(datos), 200


@app.route('/register', methods=['POST'])
def register():
    
    email = request.json.get('email')
    password = request.json.get('password')

    if not email:
        return jsonify({ "message": "Email is required"}), 400
    
    if not password:
        return jsonify({ "message": "Password is required"}), 400
    
    userFound = User.query.filter_by(email=email).first()
    if userFound:
        return jsonify({"message": "Email already in use"}), 400


    user = User(email=email, password=generate_password_hash(password))
    user.save()

    if user:
        access_token = create_access_token(identity=user.id)
        datos = {
            "access_token": access_token,
            "user": user.serialize()
        }
        return jsonify(datos), 201




@app.route('/todos', methods=['GET'])
@jwt_required() # Private Route
def get_all_todos():
    email = get_jwt_identity()
    print(email)
    todos = Task.query.all() # [<object 0x4434343>, <object 0x303030300>]
    todos = list(map(lambda task: task.serialize(), todos)) # [{id: 1, description: 'Comprar Pan', done: False }]
    return jsonify(todos), 200


@app.route('/todos', methods=['POST'])
@jwt_required() # Private Route
def add_task():
    id = get_jwt_identity()
    task_info = request.json
    if not 'description' in task_info:
        return jsonify({ "msg": "Description is required"}), 400
    if task_info["description"] == "":
        return jsonify({ "msg": "Description is required"}), 400
    
    task = Task(description=task_info["description"], users_id=id) # Creando la tarea
    db.session.add(task) # Ejecutando el INSERT
    db.session.commit() # Guardando los Cambios

    return jsonify({ "msg": "Task created successfully"}), 201


@app.route('/todos/<int:id>/complete', methods=['GET'])
@jwt_required() # Private Route
def complete_task(id):
    id = get_jwt_identity()
    task = Task.query.get(id)

    if not task:
        return jsonify({ "msg": "Task not found"}), 404
    
    task.done = True
    db.session.commit()

    return jsonify({"msg": f"Task {id} completed successfully"}), 200


@app.route('/todos/<int:id>/delete', methods=['DELETE'])
@jwt_required() # Private Route
def delete_task(id):
    users_id = get_jwt_identity()
    task = Task.query.get(id)

    if task.users_id != users_id:
        return jsonify({ "message": "You can't delete this task. You are not owner"}), 400

    if not task:
        return jsonify({ "msg": f"Task with id: {id} not found"}), 404
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({"msg": f"Task {id} deleted successfully"}), 200


with app.app_context() as context:
    db.create_all()

if __name__ == '__main__':
    app.run()