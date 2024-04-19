from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

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