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

def init_db(): # função para inicializar o banco de dados
    db = get_db() # Obtém a conexão com o banco de dados
    with current_app.open_resource('tables.sql') as f: # Abre o arquivo SQL que contém os comandos para criar as tabelas. o current_app.open_resource() é usado para abrir arquivos que estão dentro do diretório da aplicação Flask, como templates, arquivos estáticos ou scripts SQL.
        db.executescript(f.read().decode('utf8')) # Executa os comandos SQL para criar as tabelas

@click.command('init-db') # Cria um comando de linha de comando para inicializar o banco de dados
def init_db_command(): # Limpa o banco de dados e cria as tabelas
    init_db()
    click.echo('Banco de dados inicializado.')

sqlite3.register_converter( # Registra um conversor para o tipo datetime
    "timestamp",lambda v: datetime.fromisoformat(v.decode())
)
 
def init_app(app):

    app.teardown_appcontext(close_db)  # Registra a função close_db para ser chamada quando o contexto da aplicação for encerrado
    app.cli.add_command(init_db_command)  # Adiciona o comando init-db ao CLI da aplicação