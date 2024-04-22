from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class Task(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User")

    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "done": self.done,
            "user": self.user.email
        }