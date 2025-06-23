import sqlite3, mysql.connector
from datetime import datetime

import click
from flask import current_app, g


# def get_db():
#     """Conecta ao banco de dados SQLite e retorna a conexão."""
#     if 'db' not in g: # o g é um objeto global do Flask que persiste durante a requisição,ou seja, ele armazena dados que podem ser acessados em qualquer parte da aplicação durante o ciclo de vida de uma requisição.
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'], # Obtém o caminho do banco de dados a partir da configuração da aplicação
#             detect_types=sqlite3.PARSE_DECLTYPES # Permite o uso de tipos de dados como datetime, ou seja, permite acessar colunas do tipo datetime diretamente como objetos datetime em vez de strings.
#         )
#         g.db.row_factory = sqlite3.Row  # Permite acessar colunas por nome

    # return g.db

def get_db():
    if 'db' not in g:  # Verifica se já existe uma conexão com o banco de dados no contexto global g
        g.db = mysql.connector.connect(
            host = 'localhost',  # Endereço do servidor MySQL
            user = 'root',  # Nome de usuário do MySQL
            password = '',  # Senha do usuário do MySQL
            database = 'tables'  # Nome do banco de dados MySQL
        )
    return g.db  # Retorna a conexão com o banco de dados

def get_cursor():
    """Obtém um cursor para executar comandos SQL no banco de dados."""
    db = get_db()  # Obtém a conexão com o banco de dados
    return db.cursor(dictionary=True)  # Retorna um cursor que permite acessar colunas por nome

def close_db(e=None):
    """Fecha a conexão com o banco de dados, se estiver aberta."""
    db = g.pop('db', None) # Remove a conexão do contexto global g
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    with current_app.open_resource('tables.sql') as f: # Abre o arquivo SQL que contém os comandos para criar as tabelas
        sql_commands = f.read().decode('utf8').split(';') # Lê o conteúdo do arquivo, decodifica para UTF-8 e divide os comandos SQL por ponto e vírgula
        for command in sql_commands: # Itera sobre cada comando SQL
            command = command.strip() # Remove espaços em branco no início e no final do comando
            if command: # Verifica se o comando não está vazio
                cursor.execute(command) # Executa o comando SQL
    db.commit() # Confirma as alterações no banco de dados

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