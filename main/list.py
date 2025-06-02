from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,url_for,g
)

from werkzeug.exceptions import abort # abort é uma função que gera uma exceção HTTP, interrompendo o processamento da requisição e retornando um código de status HTTP específico.

from main.db import get_db 
from main.auth import login_required 

bp = Blueprint('list',__name__)

@bp.route('/')
def index():
    db = get_db()
    lista_de_tarefas = db.execute(
        'SELECT * FROM LISTAS_DE_TAREFAS JOIN USUARIOS ON LISTAS_DE_TAREFAS.Id_Usuario = USUARIOS.Id_Usuario ORDER BY Id_Lista DESC' # Consulta SQL para obter todas as listas de tarefas, juntando com a tabela de usuários para obter informações do usuário associado.
    ).fetchall()
    return render_template('list/index.html', lista_de_tarefas=lista_de_tarefas)

@bp.route('/<int:id_lista>/tarefas') # Define a rota para exibir as tarefas de uma lista específica, onde id_lista é um parâmetro inteiro que representa o ID da lista de tarefas.
@login_required
def tarefas(id_lista):
    db = get_db()
    tarefas = db.execute(
        '''SELECT id_tarefa, descricao, concluida, data_criacao, data_conclusao, Id_lista
           FROM TAREFAS WHERE Id_lista = ? ORDER BY id_tarefa DESC''',
        (id_lista,)
    ).fetchall()
    return render_template('list/tarefas.html', tarefas=tarefas)

@bp.route('/criar_lista', methods=('GET', 'POST'))
@login_required
def criar_lista():
    if request.method == 'POST':
        nome =  request.form['nome']
        db = get_db()
        erro = None
        if not nome:
            erro = 'O nome da lista de tarefas é obrigatório.'
        if erro is None:
            db.execute(
                'INSERT INTO LISTAS_DE_TAREFAS (nome, Id_Usuario) VALUES (?, ?)',
                (nome, g.user['Id_Usuario'])  # g.user é um dicionário que contém informações do usuário autenticado, como o ID do usuário.
            )
            db.commit()
            return redirect(url_for('list.index'))
        
        flash(erro)

    return render_template('list/criar.html')

@bp.route('/<int:id_lista>/editar_lista', methods=('GET', 'POST'))
@login_required
def editar_lista(id_lista):
    lista = get_lista(id_lista)  # Obtém a lista de tarefas pelo ID, sem verificar o autor, pois a edição pode ser feita por qualquer usuário autorizado.

    if request.method == 'POST':
        nome = request.form['nome']
        erro = None

        if not nome:
            erro = 'O nome da lista de tarefas é obrigatório.'
        if erro is None:
            db = get_db()
            db.execute(
                'UPDATE LISTAS_DE_TAREFAS SET nome = ? WHERE Id_Lista = ?',
                (nome, id_lista)
            )
            db.commit()
            return redirect(url_for('list.index')) # Redireciona para a página principal após a edição bem-sucedida.
        flash(erro)
    return render_template('list/editar_lista.html', lista=lista)  # Renderiza o template de edição da lista de tarefas, passando a lista obtida.

@bp.route('/<int:id_lista>/excluir_lista', methods=('POST',))
@login_required
def excluir_lista(id_lista):
    get_lista(id_lista)
    db = get_db() 
    db.execute('DELETE FROM LISTAS_DE_TAREFAS WHERE Id_Lista = ?', (id_lista,))  # Exclui a lista de tarefas pelo ID.
    db.commit()  # Confirma a exclusão no banco de dados.
    return redirect(url_for('list.index'))  # Redireciona para a página principal após a exclusão bem-sucedida.

@bp.route('/<int:id_lista>/criar-tarefa', methods=('GET', 'POST'))
@login_required
def criar_tarefa(id_lista):
    if request.method == 'POST':
        descricao = request.form['descricao']
        concluida = request.form.get('concluida') == 'on'
        data_conclusao = request.form.get('data_conclusao') or None
        erro = None

        if not descricao:
            erro = 'A descrição da tarefa é obrigatória.'
        if erro is None:
            db = get_db()
            db.execute(
                'INSERT INTO TAREFAS (descricao, concluida, data_conclusao, Id_lista) VALUES (?, ?, ?, ?)',
                (descricao, concluida, data_conclusao, id_lista)
            )
            db.commit()
            return redirect(url_for('list.tarefas', id_lista=id_lista))
        flash(erro)
    return render_template('list/criar_tarefa.html', id_lista=id_lista) # Renderiza o template de criação de tarefa, passando o ID da lista.

@bp.route('/<int:id_lista>/editar-tarefa/<int:id_tarefa>', methods=('GET', 'POST'))
@login_required
def editar_tarefa(id_lista, id_tarefa):
    tarefa = get_tarefa(id_tarefa)

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        concluida = request.form.get('concluida') == 'on'
        data_conclusao = request.form.get('data_conclusao') or None
        erro = None

        if not nome:
            erro = 'O nome da tarefa é obrigatório.'
        if erro is None:
            db = get_db()
            db.execute(
                '''UPDATE TAREFAS SET nome = ?, descricao = ?, concluida = ?, data_conclusao = ?
                   WHERE id_tarefa = ?''',
                (nome, descricao, concluida, data_conclusao, id_tarefa)
            )
            db.commit()
            return redirect(url_for('list.tarefas', id_lista=id_lista))
        
        flash(erro)
    
    return render_template('list/editar_tarefa.html', tarefa=tarefa, id_lista=id_lista)  # Renderiza o template de edição da tarefa, passando a tarefa obtida e o ID da lista.

@bp.route('/<int:id_lista>/excluir-tarefa/<int:id_tarefa>', methods=('POST',))
@login_required
def excluir_tarefa(id_lista, id_tarefa):

    get_tarefa(id_tarefa)
    db = get_db()
    db.execute('DELETE FROM TAREFAS WHERE id_tarefa = ?', (id_tarefa,))  # Exclui a tarefa pelo ID.
    db.commit()  # Confirma a exclusão no banco de dados.
    return redirect(url_for('list.tarefas', id_lista=id_lista))  # Redireciona para a página de tarefas da lista após a exclusão bem-sucedida.
    

def get_lista(id_lista, check_author=True):  # Obtém uma lista de tarefas específica pelo ID, com a opção de verificar se o usuário é o autor da lista.
    lista = get_db().execute(
        '''SELECT l.Id_Lista, l.nome, l.Id_Usuario, u.nome AS nome_usuario
           FROM LISTAS_DE_TAREFAS l
           JOIN USUARIOS u ON l.Id_Usuario = u.Id_Usuario
           WHERE l.Id_Lista = ?''',
        (id_lista,)
    ).fetchone()

    if lista is None:
        abort(404, f"Lista id {id_lista} não existe.")

    if check_author and lista['Id_Usuario'] != g.user['Id_Usuario']:
        abort(403)

    return lista

# verifica se a tarefa existe e se o usuário é o autor da tarefa, caso contrário, retorna um erro 404 ou 403.
def get_tarefa(id_tarefa, check_author=True):
    tarefa = get_db().execute(
        '''SELECT t.id_tarefa, t.descricao, t.concluida, t.data_criacao, t.data_conclusao, t.Id_lista, l.Id_Usuario
           FROM TAREFAS t
           JOIN LISTAS_DE_TAREFAS l ON t.Id_lista = l.Id_lista
           WHERE t.id_tarefa = ?''',
        (id_tarefa,)
    ).fetchone()

    if tarefa is None:
        abort(404, f"Tarefa id {id_tarefa} não existe.")

    if check_author and tarefa['Id_Usuario'] != g.user['Id_Usuario']:
        abort(403)

    return tarefa