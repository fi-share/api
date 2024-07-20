from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Materias, Cursos, Tps, Repositorios
from config import Config
import requests

app = Flask(__name__)

CORS(app)

app.config.from_object(Config)

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

if __name__ == "__main__":
    print("Starting server...")
    db.init_app(app)
    with app.app_context():
        db.create_all() # Considerar Flask Migrate para produccion
    app.run(debug=True)
    print("Started")