from flask import Flask, request, jsonify
#from flask_sqlalchemy import SQLAlchemy
from models import db, Task

app = Flask(__name__)
app.config['DEBUG'] = True
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/dbft24"
#db = SQLAlchemy(app)
db.init_app(app)

"""
class Task(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done
        }
"""



@app.route('/todos', methods=['GET'])
def get_all_todos():
    todos = Task.query.all() # [<object 0x4434343>, <object 0x303030300>]
    todos = list(map(lambda task: task.serialize(), todos)) # [{id: 1, description: 'Comprar Pan', done: False }]
    return jsonify(todos), 200


@app.route('/todos', methods=['POST'])
def add_task():
    task_info = request.json
    if not 'description' in task_info:
        return jsonify({ "msg": "Description is required"}), 400
    if task_info["description"] == "":
        return jsonify({ "msg": "Description is required"}), 400
    
    task = Task(description=task_info["description"]) # Creando la tarea
    db.session.add(task) # Ejecutando el INSERT
    db.session.commit() # Guardando los Cambios

    return jsonify({ "msg": "Task created successfully"}), 201


@app.route('/todos/<int:id>/complete', methods=['GET'])
def complete_task(id):
    task = Task.query.get(id)

    if not task:
        return jsonify({ "msg": "Task not found"}), 404
    
    task.done = True
    db.session.commit()

    return jsonify({"msg": f"Task {id} completed successfully"}), 200


@app.route('/todos/<int:id>/delete', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)

    if not task:
        return jsonify({ "msg": f"Task with id: {id} not found"}), 404
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({"msg": f"Task {id} deleted successfully"}), 200


with app.app_context() as context:
    db.create_all()

if __name__ == '__main__':
    app.run()