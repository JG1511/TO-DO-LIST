import sqlite3
from datatime import datetime

import click
from flask import current_app, g

def get_db():
    """Conecta ao banco de dados SQLite e retorna a conexão."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # Permite acessar colunas por nome

    return g.db

def close_db(e=None):
    """Fecha a conexão com o banco de dados, se estiver aberta."""
    db = g.pop('db', None) # Remove a conexão do contexto global g
    if db is not None:
        db.close()