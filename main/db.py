import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_db():
    """Conecta ao banco de dados SQLite e retorna a conexão."""
    if 'db' not in g: # o g é um objeto global do Flask que persiste durante a requisição,ou seja, ele armazena dados que podem ser acessados em qualquer parte da aplicação durante o ciclo de vida de uma requisição.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], # Obtém o caminho do banco de dados a partir da configuração da aplicação
            detect_types=sqlite3.PARSE_DECLTYPES # Permite o uso de tipos de dados como datetime, ou seja, permite acessar colunas do tipo datetime diretamente como objetos datetime em vez de strings.
        )
        g.db.row_factory = sqlite3.Row  # Permite acessar colunas por nome

    return g.db

def close_db(e=None):
    """Fecha a conexão com o banco de dados, se estiver aberta."""
    db = g.pop('db', None) # Remove a conexão do contexto global g
    if db is not None:
        db.close()