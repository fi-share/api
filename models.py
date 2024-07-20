import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Materias(db.Model):
    __tablename__ = 'materias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    cuatrimestre = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    cursos = db.relationship('Cursos')


class Cursos(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    id_materia = db.Column(db.Integer, db.ForeignKey('materias.id'))
    tps = db.relationship('Tps')


class Tps(db.Model):
    __tablename__ = 'tps'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    id_curso = db.Column(db.Integer, db.ForeignKey('cursos.id'))
    repositorios = db.relationship('Repositorios')


class Repositorios(db.Model):
    __tablename__ = 'repositorios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    titulo = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    calificacion = db.Column(db.Integer, nullable=False)
    id_usuario = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.now)
    id_tp = db.Column(db.Integer, db.ForeignKey('tps.id'))
