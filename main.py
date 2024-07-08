from flask import Flask, jsonify
from models import db, Materias, Cursos
from config import Config


app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)


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
        materias = Materias.query.limit(10).all()
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
    except Exception as error:
        print("Error: ", error)
        return jsonify({'error': 'Internal Server Error'}), 500


"""
PRE: Se espera un JSON con la siguiente estructura de la tabla Cursos en db:
{
    "id": numero_id,
    "nombre": "nombre del curso",
    "id_materia": numero_id,
    "tps": ["id": numero_id, "nombre": "nombre del tp"]
}
POST: Devuelve un JSON con todos los datos de la tabla cursos en db
"""


@app.route('/cursos', methods=['GET'])
def get_cursos():

    try:
        cursos = Cursos.query.limit(10).all()
        cursos_data = []
        for curso in cursos:
            curso_data = {
                'id': curso.id,
                'nombre': curso.nombre
            }
            cursos_data.append(curso_data)
        return jsonify({'cursos': cursos_data})
    except Exception as error:
        print("Error: ", error)
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == "__main__":
    print("Starting server...")
    with app.app_context():
        db.create_all() # Considerar Flask Migrate para produccion
    app.run(debug=True)
    print("Started")
