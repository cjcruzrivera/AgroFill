from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    isAdmin = db.Column(db.Boolean, default=False)


class Calculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    fecha = db.Column(db.DateTime)
    tipoEstructura = db.Column(db.String(1000))
    data = db.Column(db.String(1000))
    resultados = db.Column(db.String(1000))
