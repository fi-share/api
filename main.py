from flask import Flask, jsonify, abort
from models import db, Materias, Cursos, Tps
from config import Config


app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


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


if __name__ == "__main__":
    print("Starting server...")
    with app.app_context():
        db.create_all() # Considerar Flask Migrate para produccion
    app.run(debug=True)
    print("Started")
