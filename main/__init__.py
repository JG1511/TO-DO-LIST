# conterá a fábrica da aplicação e informará ao Python que o diretório flaskr deve ser tratado como um pacote.
import os
from flask import Flask

def create_app(test_config=None):
    # Cria a instância da aplicação
    app = Flask(__name__, instance_relative_config=True)
    
    # Configura o aplicativo

    # O app.config.from_mapping() é usado para definir configurações padrão
    # e o app.config.from_pyfile() é usado para carregar configurações de um arquivo.app

    app.config.from_mapping(
        SECRET_KEY='batman', # Chave secreta para proteger sessões e cookies
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), # Caminho do banco de dados SQLite
    )

    if test_config is None:
        # Carrega a configuração padrão
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carrega a configuração de teste
        app.config.from_mapping(test_config)

    # Garante que a pasta de instância exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Ola, mundo do Batman!'

    return app

