# db.py
import uuid
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create app and config BEFORE using db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackathon.sqlite3'  # file created in cwd
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Keep your style: create SQLAlchemy instance without app, then init_app
db = SQLAlchemy()
db.init_app(app)

# ======= models =======
class Userers(db.Model):
    __tablename__ = 'auth_users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<Userers {self.id} {self.email} {self.username}>"

class Registration(db.Model):
    __tablename__ = 'registrations'
    reg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.String(36), db.ForeignKey('auth_users.id'), nullable=False)
    event_name = db.Column(db.String(255), nullable=False)
    team_name = db.Column(db.String(255), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    reg_date = db.Column(db.String(255), nullable=False)
    member1_name = db.Column(db.String(255), nullable=True)
    member1_phone = db.Column(db.String(20), nullable=True)
    member2_name = db.Column(db.String(255), nullable=True)
    member2_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('Userers', backref=db.backref('registrations', lazy='dynamic'))
    event = db.relationship('Event', backref=db.backref('registrations', lazy='dynamic'))

    def __repr__(self):
        return f"<Registration {self.reg_id} user={self.userid} event={self.event_id}>"

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    last_date = db.Column(db.String(100), nullable=True)
    event_upload_date = db.Column(db.String(100), nullable=True)
    creator = db.Column(db.String(36), db.ForeignKey('auth_users.id'), nullable=True)
    prize1 = db.Column(db.String(255), nullable=True)
    prize2 = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    creator_user = db.relationship('Userers', backref=db.backref('events_created', lazy='dynamic'))

    def __repr__(self):
        cols = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return f"<Event {cols}>"


class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Admin {self.admin_id} {self.name}>"

# ======= create tables when running directly =======
if __name__ == '__main__':
    # Creates the SQLite file and all tables in the configured path
    with app.app_context():
        db.create_all()
    print("Database and tables created successfully!")
