import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash # check_password_hash é usado para verificar se a senha fornecida corresponde à senha armazenada de forma segura, enquanto generate_password_hash é usado para criar uma versão criptografada da senha.

from main.db import get_db # get_db é uma função que retorna a conexão com o banco de dados, permitindo acessar as tabelas e executar consultas SQL.
bp = Blueprint('auth', __name__, url_prefix='/auth') # Define um Blueprint chamado 'auth' com o prefixo '/auth', permitindo organizar rotas relacionadas à autenticação.

@bp.route('/registro', methods=('GET', 'POST')) # Define a rota para o registro de usuários, aceitando métodos GET e POST.
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        db = get_db()
        erro = None

        if not usuario:
            erro = 'Usuário é obrigatório.'
        elif not senha:
            erro = 'Senha é obrigatória.'

        if erro is None:
            try:
                db.execute( # Executa uma consulta SQL para inserir um novo usuário no banco de dados.
                    'INSERT INTO usuario (usuario, senha) VALUES (?, ?)',
                    (usuario, generate_password_hash(senha))
                )
                db.commit()
            except db.IntegrityError: # IntegrityError é uma exceção que ocorre quando há uma violação de integridade no banco de dados, como tentar inserir um valor duplicado em uma coluna com restrição de unicidade.
                erro = f'Usuário {usuario} já existe.'
            else:
                return redirect(url_for('auth.login'))
        flash(erro)
    return render_template('auth/registro.html')