from flask import Flask
from .main import main as main_blueprint


def create_app():
    """Cria a instância do aplicativo"""
    app = Flask(__name__)

    # Essa key é usada como base para criptografar senhas ao usar um login no aplicativo
    # Ela é setada aqui, mas, como o aplicativo não usa o flask_login, não é obrigatório
    # Porém, já a deixei pronta para uso, caso necessário
    app.secret_key = """290e0e0bb7c119bc4a8316495fe90d8b07fcf5cbe24ab1e0a470b957878e72bc
                        5d95a8a46f2ba775e53aabf6e9698cd6ac1e00cc6d8b98911b3f09ebf7d94228
                        9772b7b537fd00cfca3697c451b2bc23a13095d4699d2e9e63fd1039e8a0e8db
                        d6220a8f1c2c18630f6a927f28af357e3303d45410210778a8045a4b1c9e6a61
                        af2d846451149a8548c6151d8775fbec0d51f4cb548485dc69b8f4753d916b3a
                        a63492f362e20b0d5f31cc93efcf11a5548ada22c350737eb8e70a1ca3ba514b
                        66d3268b2002804147447e5a9a4700bab3d264f5c6db9dcb084e26e5d89a7af8
                        08f5eeb8815f14960125ad78fcc4e6264d9e57d3adba8ee157ddd39c27ec5500
                        a15a1e9beecd5205d904da886dcc2954a1ac01779ec1156891e02ef6bc68b043
                        ec73248f7dc5d6ab7af12d1fe219abae4fcc294417ba29d905d6f5763ccab543"""

    app.register_blueprint(main_blueprint)

    return app
