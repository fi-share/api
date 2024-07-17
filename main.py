from flask import Flask, jsonify, abort, request
from models import db, Materias, Cursos, Tps, Repositorios
from datetime import datetime
from config import Config


app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/")
def home():
    return "Hello World"


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
        materias_data = []
        for materia in materias:
            materia_data = {
                'id': materia.id,
                'nombre': materia.nombre,
                'cuatrimestre': materia.cuatrimestre,
                'anio': materia.anio,
                'cursos': []
            }
            for curso in materia.cursos:
                curso_data = {
                    'id': curso.id,
                    'nombre': curso.nombre,

                }
                materia_data['cursos'].append(curso_data)
            materias_data.append(materia_data)
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

POST: Devuelve un JSON con todos los datos de la tabla cursos con el id dado incluyendo los tps asociados
"""


@app.route('/cursos/<int:id_curso>', methods=['GET'])
def get_curso_tps(id_curso):

    try:
        curso = Cursos.query.get(id_curso)
        if curso is None:
            abort(404, description="Resource not found")

        tps_data = [{'id': tp.id, 'nombre': tp.nombre, 'descripcion': tp.descripcion} for tp in curso.tps]

        curso_data = {
            'id': curso.id,
            'nombre': curso.nombre,
            'tps': tps_data
        }
        return jsonify({'curso': curso_data})
    except Exception:
        abort(500, description="Internal Server Error")


"""   
PRE: Se espera un id de TP válido
POST: Devuelve un JSON con los datos del TP y sus repositorios asociados
"""


@app.route('/tps/<int:id_tp>', methods=['GET'])
def get_tp_repositorios(id_tp):
    try:
        tp = Tps.query.get(id_tp)
        if tp is None:
            abort(404, description="Resource not found")

        repositorios_data = [{'id': repo.id, 'full_name': repo.full_name, 'descripcion': repo.descripcion,
                              'calificacion': repo.calificacion, 'id_usuario': repo.id_usuario,
                              'fecha_creacion': repo.fecha_creacion.isoformat()} for repo in tp.repositorios]
        tp_data = {
            'id': tp.id,
            'nombre': tp.nombre,
            'descripcion': tp.descripcion,
            'repositorios': repositorios_data
        }

        return jsonify({'tp': tp_data})
    except Exception:
        abort(500, description="Internal Server Error")


"""
PRE: Se espera un JSON con los datos del repositorio y un id_tp válido en la URL.
POST: Devuelve un JSON con los datos del repositorio creado o un mensaje de error.
"""


@app.route('/tps/<int:id_tp>/repositorios', methods=['POST'])
def compartir_public_repository(id_tp):

    try:
        tp = Tps.query.get(id_tp)
        if tp is None:
            abort(404, description="Resource not found")

        data = request.json
        if not data:
            abort(400, description="Bad Request")

        columns_name = ['full_name', 'descripcion', 'id_usuario']
        for name in columns_name:
            if name not in data:
                abort(400, description="Bad Request")

        nuevo_repositorio = Repositorios(
            full_name=data['full_name'],
            descripcion=data['descripcion'],
            calificacion=data.get('calificacion', 0),
            id_usuario=data['id_usuario'],
            fecha_creacion=datetime.now(),
            id_tp=id_tp
        )

        db.session.add(nuevo_repositorio)
        db.session.commit()

        response_data = {
            'id': nuevo_repositorio.id,
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


@app.route('/tps/<int:id_tp>/repositorios/<int:id_repositorio>', methods=['PATCH', 'DELETE'])
def up_and_delete_repository(id_tp, id_repositorio):

    try:
        tp = Tps.query.get(id_tp)
        if tp is None:
            abort(404, description="Resource not found")

        repositorio = Repositorios.query.filter_by(id=id_repositorio, id_tp=id_tp).first()
        if repositorio is None:
            abort(404, description="Resource not found")

        if request.method == 'DELETE':
            db.session.delete(repositorio)
            db.session.commit()

            return jsonify({'message': f'Repositorio con ID {id_repositorio} eliminado exitosamente'}), 200

        data = request.json
        if not data:
            abort(400, description="Bad Requests")

        if 'full_name' in data:
            repositorio.full_name = data['full_name']
        if 'descripcion' in data:
            repositorio.descripcion = data['descripcion']
        if 'calificacion' in data:
            repositorio.calificacion = data['calificacion']
        if 'id_usuario' in data:
            repositorio.id_usuario = data['id_usuario']

        db.session.commit()

        response_data = {
            'id': repositorio.id,
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
