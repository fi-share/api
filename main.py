from flask import Flask
from models import db, Materias, Cursos, Tps, Repositorios
from config import Config

app = Flask(__name__)

app.config.from_object(Config)


@app.route("/")
def home():
    return "Hello World"


if __name__ == "__main__":
    print("Starting server...")
    db.init_app(app)
    with app.app_context():
        db.create_all() # Considerar Flask Migrate para produccion
    app.run(debug=True)
    print("Started")