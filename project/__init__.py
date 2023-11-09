from flask import Flask
from .main import main as main_blueprint


def create_app():
    """Cria a instância do app"""
    app = Flask(__name__)

    app.secret_key = "É-ISSO-AI"

    app.register_blueprint(main_blueprint)

    return app
