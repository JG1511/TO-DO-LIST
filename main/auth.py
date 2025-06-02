import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash # check_password_hash é usado para verificar se a senha fornecida corresponde à senha armazenada de forma segura, enquanto generate_password_hash é usado para criar uma versão criptografada da senha.

from main.db import get_db # get_db é uma função que retorna a conexão com o banco de dados, permitindo acessar as tabelas e executar consultas SQL.
bp = Blueprint('auth', __name__, url_prefix='/auth') # Define um Blueprint chamado 'auth' com o prefixo '/auth', permitindo organizar rotas relacionadas à autenticação.

@bp.route('/registro', methods=('GET', 'POST')) # Define a rota para o registro de usuários, aceitando métodos GET e POST.
def registro():
    if request.method == 'POST': # Verifica se o método da requisição é POST, indicando que o formulário foi enviado.
        # Obtém os dados do formulário de registro.
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
                    'INSERT INTO USUARIOS (nome, senha) VALUES (?, ?)',
                    (usuario, generate_password_hash(senha)) # generate_password_hash é usado para criar uma versão criptografada da senha antes de armazená-la no banco de dados.
                )
                db.commit()
            except db.IntegrityError: # IntegrityError é uma exceção que ocorre quando há uma violação de integridade no banco de dados, como tentar inserir um valor duplicado em uma coluna com restrição de unicidade.
                erro = f'Usuário {usuario} já existe.'
            else:
                return redirect(url_for('auth.login'))
        flash(erro)
    return render_template('auth/registro.html')

bp.route('/login',methods=('GET', 'POST')) # Define a rota para o login de usuários
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        db = get_db()
        erro = None
        usuario_db = db.execute(
            'SELECT  Id_Usuario, nome, senha FROM USUARIOS WHERE nome = ?',
            (usuario,)
        ).fetchone() # fetchone() é usado para recuperar uma única linha do resultado da consulta SQL, que corresponde ao usuário fornecido.
        if usuario_db is None:
            erro = 'Usuário não encontrado.'
        elif not check_password_hash(usuario_db['senha'], senha): # check_password_hash é usado para verificar se a senha fornecida corresponde à senha armazenada de forma segura.
            erro = 'Senha incorreta.'
        
        if erro is None:
            session.clear()
            session['Id_Usuario'] = usuario_db['Id_Usuario'] # Armazena o ID do usuário na sessão para manter o estado de autenticação.
            return redirect(url_for('index')) # Redireciona para a página inicial após o login bem-sucedido.
        
        flash(erro) # Exibe uma mensagem de erro se houver problemas com o login.
    
    return render_template('auth/login.html') # Renderiza o template de login se o método for GET ou se houver erros no POST.