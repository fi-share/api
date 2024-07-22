from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from models import db, Materias, Cursos, Tps, Repositorios
from datetime import datetime
from config import Config
import requests
import markdown

app = Flask(__name__)

CORS(app)

app.config.from_object(Config)
db.init_app(app)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), f"500 {e.description}"


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), f"400 {e.description}"


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), f"404 {e.description}"


@app.route("/")
def home():
    return "Hello World"


@app.route('/exchange-code', methods=['POST'])
def exchange_code():
    try:
        if 'code' not in request.json:
                return jsonify({'error': 'Falta el parametro "code"'}), 400
        
        token_response = requests.post('https://github.com/login/oauth/access_token', data={
            'client_id': app.config["GITHUB_CLIENT_ID"],
            'client_secret': app.config["GITHUB_CLIENT_SECRET"],
            'code': request.json['code'],
            'redirect_uri': request.json['redirect_uri']
        }, headers={'Accept': 'application/json'})

        if token_response.status_code != 200:
            return jsonify({'error': 'Error de github'}), token_response.status_code

        token_response_json = token_response.json()
        return jsonify(token_response_json)
    except Exception as err:
        return jsonify({'error': str(err)}), 500

"""
PRE: Se espera un JSON con la siguiente estructura de la tabla Materia en db:
{
    "id": numero_id,
    "nombre": "nombre de la materia",
    "cuatrimestre": 1 o 2,
    "anio": 2024,
    "cursos": ["id": numero_id, "nombre": "nombre del curso"]
}
POST: Devuelve un JSON con todos los datos de la tabla materias en db
"""


@app.route('/materias', methods=['GET'])
def get_materias():
    try:
        materias = Materias.query.all()
        materias_data = [{
                'id': materia.id,
                'nombre': materia.nombre,
                'cuatrimestre': materia.cuatrimestre,
                'anio': materia.anio,
            } for materia in materias]
            
        return jsonify({'materias': materias_data})
    except Exception:
        abort(500, description="Internal Server Error")


"""
PRE: Se espera un id de la tabla materia válido
POST: Devuelve un JSON con los datos de la materia y sus cursos asociados
"""


@app.route('/materias/<int:id_materia>', methods=['GET'])
def get_materia_cursos(id_materia):
    try:
        materia = Materias.query.get(id_materia)
        if materia is None:
            abort(404, description="Resource not found")

        cursos_data = [{'id': curso.id, 'nombre': curso.nombre} for curso in materia.cursos]

        materia_data = {
            'id': materia.id,
            'nombre': materia.nombre,
            'cuatrimestre': materia.cuatrimestre,
            'anio': materia.anio,
            'cursos': cursos_data
        }

        return jsonify({'materia': materia_data})
    except Exception:
        abort(500, description="Internal Server Error")


"""
PRE: Se espera un id valido de la tabla cursos

POST: Devuelve un JSON con todos los datos de la tabla cursos y su materia asociada. 
      Con el id dado incluyendo los tps...
"""


@app.route('/cursos/<int:id_curso>', methods=['GET'])
def get_curso_tps(id_curso):

    try:
        curso = Cursos.query.get(id_curso)
        if curso is None:
            abort(404, description="Resource not found")

        materia = curso.materia

        tps_data = [{'id': tp.id, 'nombre': tp.nombre, 'descripcion': tp.descripcion} for tp in curso.tps]

        curso_data = {
            'id': curso.id,
            'nombre': curso.nombre,
            'tps': tps_data,
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
                'cuatrimestre': materia.cuatrimestre,
                'anio': materia.anio
            }
        }
        return jsonify({'curso': curso_data})
    except Exception:
        abort(500, description="Internal Server Error")


"""   
PRE: Se espera un id de TP válido
POST: Devuelve un JSON con los datos del TP, curso, materia y repositorios asociados
"""


@app.route('/tps/<int:id_tp>', methods=['GET'])
def get_tp_data(id_tp):
    try:
        tp = Tps.query.get(id_tp)
        if tp is None:
            abort(404, description="Resource not found")

        curso = tp.curso
        materia = curso.materia

        tp_data = {
            'id': tp.id,
            'nombre': tp.nombre,
            'curso': {
                'id': curso.id,
                'nombre': curso.nombre
            },
            'materia': {
                'id': materia.id,
                'nombre': materia.nombre,
            }
        }

        return jsonify(tp_data)
    except Exception:
        abort(500, description="Internal Server Error")

@app.route('/tps/<int:id_tp>/descripcion_html', methods=['GET'])
def get_tp_descripcion_html(id_tp):
    try:
        tp = Tps.query.get(id_tp)
        if tp is None:
            abort(404, description="Resource not found")

        descripcion_html = markdown.markdown(tp.descripcion)

        return descripcion_html
    except Exception:
        abort(500, description="Internal Server Error")

@app.route('/tps/<int:id_tp>/repositorios', methods=['GET'])
def get_tp_repositorios(id_tp):
    try:
        repositorios = Repositorios.query.filter_by(id_tp=id_tp).all()

        repositorios_data = [{
            'id': repo.id, 
            'titulo':repo.titulo, 
            'full_name': repo.full_name, 
            'descripcion': repo.descripcion,
            'calificacion': repo.calificacion, 
            'id_usuario': repo.id_usuario,
            'fecha_creacion': repo.fecha_creacion.isoformat()
        } for repo in repositorios]
        
        return jsonify(repositorios_data)
    except Exception:
        abort(500, description="Internal Server Error")


"""
PRE: Se espera un JSON con los datos del repositorio y un id_tp válido en la URL.
POST: Devuelve un JSON con los datos del repositorio creado o un mensaje de error.
"""


@app.route('/tps/<int:id_tp>/repositorios', methods=['POST'])
def compartir_public_repository(id_tp):

    tp = Tps.query.get(id_tp)
    if tp is None:
        abort(404, description="Resource not found")

    data = request.form
    if not data:
        abort(400, description="Bad Request")

    columns_name = ['full_name', 'titulo', 'id_usuario', 'id']
    for name in columns_name:
        if name not in data:
            abort(400, description=f"Missing required field: {name}")

    repositorio_exist = Repositorios.query.get(data['id'])
    print(repositorio_exist)
    if repositorio_exist:
        abort(400, description="Repository already exists")

    try:
        nuevo_repositorio = Repositorios(
            id=data['id'],
            titulo=data['titulo'],
            full_name=data['full_name'],
            descripcion=data.get('descripcion', ''),
            calificacion=data.get('calificacion', 0),
            id_usuario=data['id_usuario'],
            fecha_creacion=datetime.now(),
            id_tp=id_tp
        )

        db.session.add(nuevo_repositorio)
        db.session.commit()

        response_data = {
            'id': nuevo_repositorio.id,
            'titulo': nuevo_repositorio.titulo,
            'full_name': nuevo_repositorio.full_name,
            'descripcion': nuevo_repositorio.descripcion,
            'calificacion': nuevo_repositorio.calificacion,
            'id_usuario': nuevo_repositorio.id_usuario,
            'fecha_creacion': nuevo_repositorio.fecha_creacion.isoformat(),
            'id_tp': nuevo_repositorio.id_tp
        }

        return jsonify(response_data), 201

    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")


"""
Para metodos PATH o DELETE se espera un id_tp y un id_repositorio válidos en la URL...

PRE: Se espera un JSON con los datos a actualizar, un id_tp y un id_repositorio válidos en la URL.
POST: Devuelve un JSON con los datos actualizados del repositorio o un mensaje de error.

"""


@app.route('/tps/<int:id_tp>/repositorios/<int:id_repositorio>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def up_and_delete_repository(id_tp, id_repositorio):

    try:
        tp = Tps.query.get(id_tp)
        if tp is None:
            abort(404, description="Resource not found")

        repositorio = Repositorios.query.filter_by(id=id_repositorio, id_tp=id_tp).first()
        if repositorio is None:
            abort(404, description="Resource not found")

        if request.method == 'GET':
            response_data = {
                'id': repositorio.id,
                'titulo': repositorio.titulo,
                'full_name': repositorio.full_name,
                'descripcion': repositorio.descripcion,
                'calificacion': repositorio.calificacion,
                'id_usuario': repositorio.id_usuario,
                'fecha_creacion': repositorio.fecha_creacion.isoformat(),
                'id_tp': repositorio.id_tp
            }
            return jsonify(response_data), 200

        elif request.method == 'PUT':
            data = request.form
            if not data:
                abort(400, description="Bad Request")

            required_fields = ['titulo', 'descripcion']
            for field in required_fields:
                if field not in data:
                    abort(400, description=f"Missing required field: {field}")

            # no actualizamos fecha_creacion ni id_tp
            repositorio.titulo = data['titulo']
            repositorio.descripcion = data['descripcion']

            db.session.commit()

        elif request.method == 'PATCH':
            data = request.form
            if 'calificacion' not in data:
                abort(400, description="PATCH solo admite calificacion")

            repositorio.calificacion = data['calificacion']

            db.session.commit()

        elif request.method == 'DELETE':
            db.session.delete(repositorio)
            db.session.commit()
            return jsonify({'message': f'Sucess: {id_repositorio} was deleted'}), 200

        else:
            abort(400, description="Bad Request")

        response_data = {
            'id': repositorio.id,
            'titulo': repositorio.titulo,
            'full_name': repositorio.full_name,
            'descripcion': repositorio.descripcion,
            'calificacion': repositorio.calificacion,
            'id_usuario': repositorio.id_usuario,
            'fecha_creacion': repositorio.fecha_creacion.isoformat(),
            'id_tp': repositorio.id_tp
        }

        return jsonify(response_data), 200

    except Exception:
        db.session.rollback()
        abort(500, description="Internal Server Error")


if __name__ == "__main__":
    print("Starting server...")
    with app.app_context():
        db.create_all()  # Considerar Flask Migrate para produccion
    app.run(debug=True)
    print("Started")
