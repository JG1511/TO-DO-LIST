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
        email = request.form['email']
        senha = request.form['senha']
        db = get_db()
        erro = None

        if not usuario:
            erro = 'Usuário é obrigatório.'
        elif not email:
            erro = 'Email é obrigatório.'
        elif not senha:
            erro = 'Senha é obrigatória.'

        if erro is None:
            try:
                db.execute( # Executa uma consulta SQL para inserir um novo usuário no banco de dados.
                    'INSERT INTO USUARIOS (nome, email, senha) VALUES (?, ?, ?)',
                    (usuario,email, generate_password_hash(senha)) # generate_password_hash é usado para criar uma versão criptografada da senha antes de armazená-la no banco de dados.
                )
                db.commit()
            except db.IntegrityError: # IntegrityError é uma exceção que ocorre quando há uma violação de integridade no banco de dados, como tentar inserir um valor duplicado em uma coluna com restrição de unicidade.
                erro = f'Usuário {usuario} já existe.'
            else:
                return redirect(url_for('auth.login'))
        flash(erro)
    return render_template('auth/registro.html')

@bp.route('/usuarios') # Define a rota para listar todos os usuários registrados.
def listar_usuarios():
    db = get_db()
    usuarios = db.execute(
        'SELECT Id_Usuario, nome, email FROM USUARIOS ORDER BY Id_Usuario DESC' # Consulta SQL para obter todos os usuários, ordenados pelo ID do usuário em ordem decrescente.
    ).fetchall()
    return render_template('auth/usuarios.html', usuarios=usuarios) # Renderiza o template de listagem de usuários, passando a lista de usuários obtida do banco de dados.

@bp.route('/<int:id_usuario>/editar', methods=('GET', 'POST')) # Define a rota para editar um usuário específico, onde id_usuario é um parâmetro inteiro que representa o ID do usuário.
def editar_usuario(id_usuario):
    usuario = get_user(id_usuario)  # Obtém o usuário pelo ID, garantindo que o usuário exista.
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        erro = None

        if not nome:
            erro = 'Nome é obrigatório.'
        elif not email: 
            erro = 'Email é obrigatório.'
        elif not senha:
            erro = 'Senha é obrigatória.'
        if erro is None:
            db = get_db()
            db.execute(
                'UPDATE USUARIOS SET nome = ?, email = ?, senha = ? WHERE Id_Usuario = ?',(nome, email, generate_password_hash(senha), id_usuario) # Atualiza os dados do usuário no banco de dados, incluindo a senha criptografada.
            )
            db.commit()
            return redirect(url_for('auth.listar_usuarios')) # Redireciona para a lista de usuários após a edição bem-sucedida.
        flash(erro)
    return render_template('auth/editar_usuario.html', usuario=usuario)  # Renderiza o template de edição de usuário, passando o usuário obtido.

@bp.route('/<int:id_usuario>/deletar', methods=('POST',)) # Define a rota para deletar um usuário específico, onde id_usuario é um parâmetro inteiro que representa o ID do usuário.
def deletar_usuario(id_usuario):
    db = get_db()
    db.execute(
        'DELETE FROM USUARIOS WHERE Id_Usuario = ?',(id_usuario,) # Executa uma consulta SQL para deletar o usuário do banco de dados com base no ID fornecido.
    )
    db.commit()
    return redirect(url_for('auth.listar_usuarios'))  # Redireciona para a lista de usuários após a exclusão bem-sucedida.

@bp.route('/login',methods=('GET', 'POST')) # Define a rota para o login de usuários
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        db = get_db()
        erro = None
        usuario_db = db.execute(
            'SELECT  Id_Usuario, nome, senha FROM USUARIOS WHERE nome = ?',
            (usuario,)
        ).fetchone() # fetchone() é usado para recuperar uma única linha do resultado da consulta SQL, que corresponde ao usuário fornecido. E o fatchall retorna todas as linhas do resultado da consulta SQL, que corresponde ao usuário fornecido.
        if usuario_db is None:
            erro = 'Usuário não encontrado.'
        elif not check_password_hash(usuario_db['senha'], senha): # check_password_hash é usado para verificar se a senha fornecida corresponde à senha armazenada de forma segura.
            erro = 'Senha incorreta.'
        
        if erro is None:
            # session é um dicionário que armazena dados temporários do usuário durante a sessão atual, permitindo manter o estado entre requisições.
            session.clear()
            session['Id_Usuario'] = usuario_db['Id_Usuario'] # Armazena o ID do usuário na sessão para manter o estado de autenticação.
            return redirect(url_for('index')) # Redireciona para a página inicial após o login bem-sucedido.
        
        flash(erro) # Exibe uma mensagem de erro se houver problemas com o login.
    
    return render_template('auth/login.html') # Renderiza o template de login se o método for GET ou se houver erros no POST.

@bp.before_app_request # Decorador que executa a função antes de cada requisição da aplicação.
def load_logged_in_user(): 
    """Carrega o usuário autenticado na sessão."""
    user_id = session.get('Id_Usuario')

    if user_id is None:
        g.user = None # Se não houver ID de usuário na sessão, define g.user como None.
    else:
        g.user = get_db().execute(
            'SELECT * FROM USUARIOS WHERE Id_Usuario = ?', (user_id,)
        ).fetchone()  # Caso contrário, busca o usuário no banco de dados usando o ID armazenado na sessão.

@bp.route('/logout') # Define a rota para o logout do usuário.
def logout():
    session.clear()  # Limpa todos os dados da sessão, efetivamente desconectando o usuário.
    return redirect(url_for('auth.login'))  # Redireciona para a página inicial após o logout.

def login_required(view): # O decorator login_required pode ser aplicado a qualquer rota que exija autenticação, garantindo que apenas usuários autenticados possam acessá-la.
    """Decorator para exigir que o usuário esteja autenticado para acessar uma rota."""
    @functools.wraps(view)  # Preserva as informações da função original, como nome e docstring.
    def wrapped_view(**kwargs): # Função interna que verifica se o usuário está autenticado antes de chamar a função original.
        if g.user is None:  # Verifica se o usuário está autenticado.au
            return redirect(url_for('auth.login'))  # Se não estiver autenticado, redireciona para a página de login.
        return view(**kwargs)  # Se estiver autenticado, chama a função original.

    return wrapped_view  # Retorna a função interna como o novo decorator, que pode ser aplicado a outras rotas.


def get_user(id_usuario):
    """Obtém um usuário pelo ID."""
    user = get_db().execute(
        'SELECT * FROM USUARIOS WHERE Id_Usuario = ?', (id_usuario,)
    ).fetchone()  # Busca o usuário no banco de dados pelo ID fornecido.
    if user is None:
        abort(404, f'Usuário id {id_usuario} não encontrado.')  # Se o usuário não for encontrado, retorna um erro 404.
    return user  # Retorna o usuário encontrado.