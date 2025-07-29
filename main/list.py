from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,url_for,g
)

from werkzeug.exceptions import abort # abort é uma função que gera uma exceção HTTP, interrompendo o processamento da requisição e retornando um código de status HTTP específico.

from main.db import get_db , get_cursor
from main.auth import login_required 

bp = Blueprint('list',__name__)

@bp.route('/')
def index():
    db = get_db()
    cursor = get_cursor()
    # lista_de_tarefas = db.execute(
    #     'SELECT * FROM LISTAS_DE_TAREFAS INNER JOIN USUARIOS ON LISTAS_DE_TAREFAS.Id_Usuario = USUARIOS.Id_Usuario ORDER BY Id_Lista DESC' # Consulta SQL para obter todas as listas de tarefas, juntando com a tabela de usuários para obter informações do usuário associado.
    # ).fetchall()

    cursor.execute(
         'SELECT * FROM LISTAS_DE_TAREFAS INNER JOIN USUARIOS ON LISTAS_DE_TAREFAS.Id_Usuario = USUARIOS.Id_Usuario ORDER BY Id_Lista DESC' # Consulta SQL para obter todas as listas de tarefas, juntando com a tabela de usuários para obter informações do usuário associado.
    )
    lista_de_tarefas = cursor.fetchall()  # Obtém todas as listas de tarefas do usuário autenticado.
    return render_template('list/index.html', lista_de_tarefas=lista_de_tarefas)

@bp.route('/<int:id_lista>/tarefas') # Define a rota para exibir as tarefas de uma lista específica, onde id_lista é um parâmetro inteiro que representa o ID da lista de tarefas.
@login_required
def tarefas(id_lista):
    db = get_db()
    cursor = get_cursor()
    # tarefas = db.execute(
    #     '''SELECT id_tarefa, descricao, concluida, data_criacao, data_conclusao, Id_lista
    #        FROM TAREFAS WHERE Id_lista = %s ORDER BY id_tarefa DESC''',
    #     (id_lista,)
    # ).fetchall()
    cursor.execute(
         '''SELECT id_tarefa, descricao, concluida, data_criacao, data_conclusao, Id_lista
           FROM TAREFAS WHERE Id_lista = %s ORDER BY id_tarefa DESC''',
        (id_lista,)
    )
    tarefas = cursor.fetchall()  # Obtém todas as tarefas da lista de tarefas especificada pelo ID.
    return render_template('list/tarefas.html', tarefas=tarefas)

@bp.route('/criar_lista', methods=('GET', 'POST'))
@login_required
def criar_lista():
    if request.method == 'POST':
        nome =  request.form['nome']
        db = get_db()
        cursor = get_cursor()
        erro = None
        if not nome:
            erro = 'O nome da lista de tarefas é obrigatório.'
        if erro is None:
            # db.execute(
            #     'INSERT INTO LISTAS_DE_TAREFAS (nome, Id_Usuario) VALUES (%s, %s)',
            #     (nome, g.user['Id_Usuario'])  # g.user é um dicionário que contém informações do usuário autenticado, como o ID do usuário.
            # )
            cursor.execute(
                 'INSERT INTO LISTAS_DE_TAREFAS (nome, Id_Usuario) VALUES (%s, %s)',
            #     (nome, g.user['Id_Usuario'])  # g.user é um dicionário que contém informações do usuário autenticado, como o ID do usuário.
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
            cursor = get_cursor()
            # db.execute(
            #     'UPDATE LISTAS_DE_TAREFAS SET nome = %s WHERE Id_Lista = %s',
            #     (nome, id_lista)
            # )
            cursor.execute(
                'UPDATE LISTAS_DE_TAREFAS SET nome = %s WHERE Id_Lista = %s',
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
    cursor = get_cursor()
    # db.execute('DELETE FROM LISTAS_DE_TAREFAS WHERE Id_Lista = %s', (id_lista,))  # Exclui a lista de tarefas pelo ID.
    cursor.execute('DELETE FROM TAREFAS WHERE Id_lista = %s', (id_lista,))  # Exclui todas as tarefas associadas à lista de tarefas.
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
        cursor = get_cursor()

        if not descricao:
            erro = 'A descrição da tarefa é obrigatória.'
        if erro is None:
            db = get_db()
            # db.execute(
            #     'INSERT INTO TAREFAS (descricao, concluida, data_conclusao, Id_lista) VALUES (%s, %s, %s, %s)',
            #     (descricao, concluida, data_conclusao, id_lista)
            # )
            cursor.execute(
                 'INSERT INTO TAREFAS (descricao, concluida, data_conclusao, Id_lista) VALUES (%s, %s, %s, %s)',
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
        descricao = request.form['descricao']
        concluida = request.form.get('concluida') == 'on'
        data_conclusao = request.form.get('data_conclusao') or None
        erro = None

        cursor = get_cursor()

        if erro is None:
            db = get_db()
            # db.execute(
            #     '''UPDATE TAREFAS SET descricao = %s, concluida = %s, data_conclusao = %s
            #        WHERE id_tarefa = %s''',
            #     ( descricao, concluida, data_conclusao, id_tarefa)
            # )
            cursor.execute(
                '''UPDATE TAREFAS SET descricao = %s, concluida = %s, data_conclusao = %s
                    WHERE id_tarefa = %s''',
                    ( descricao, concluida, data_conclusao, id_tarefa)
            )
            db.commit()
            return redirect(url_for('list.tarefas', id_lista=id_lista))
        
        flash(erro)
    
    return render_template('list/editar_tarefa.html', tarefa=tarefa, id_lista=id_lista)  # Renderiza o template de edição da tarefa, passando a tarefa obtida e o ID da lista.

@bp.route('/<int:id_lista>/excluir-tarefa/<int:id_tarefa>', methods=('POST',))
@login_required
def excluir_tarefa(id_lista, id_tarefa):

    get_tarefa(id_tarefa)
    cursor = get_cursor()
    db = get_db()
    # db.execute('DELETE FROM TAREFAS WHERE id_tarefa = %s', (id_tarefa,))  # Exclui a tarefa pelo ID.
    cursor.execute('DELETE FROM TAREFAS WHERE id_tarefa = %s', (id_tarefa,))  # Exclui a tarefa pelo ID.
    db.commit()  # Confirma a exclusão no banco de dados.
    return redirect(url_for('list.tarefas', id_lista=id_lista))  # Redireciona para a página de tarefas da lista após a exclusão bem-sucedida.
    
@bp.route('/tarefa-concluida')
@login_required
def tarefa_concluida():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM tarefas_concluidas_view WHERE Id_Usuario = %s", (g.user['Id_Usuario'],))
    tarefas_concluidas = cursor.fetchall()  # Obtém todas as tarefas concluídas do usuário autenticado.
    return render_template('list/tarefa_concluida.html', tarefas_concluidas=tarefas_concluidas)  # Renderiza o template de tarefas concluídas, passando as tarefas obtidas.

@bp.route('/<int:id_lista>/total_pendentes')
@login_required
def total_pendentes(id_lista):
    cursor = get_cursor()
    cursor.execute("SELECT contar_tarefas_pendentes(%s)", (id_lista,))
    total = cursor.fetchone()[0]
    return render_template('list/total_pendentes.html', total=total, id_lista=id_lista)

@bp.route('/<int:id_lista>/concluir_todas', methods=['POST'])
@login_required
def concluir_todas(id_lista):
    db = get_db()
    cursor = get_cursor()
    cursor.execute("CALL concluir_todas_tarefas(%s)", (id_lista,))
    db.commit()
    flash('Todas as tarefas da lista foram concluídas!')
    return redirect(url_for('list.tarefas', id_lista=id_lista))

def get_lista(id_lista, check_author=True):  # Obtém uma lista de tarefas específica pelo ID, com a opção de verificar se o usuário é o autor da lista.



    cursor = get_cursor()

    # lista = get_db().execute(
    #     '''SELECT l.Id_Lista, l.nome, l.Id_Usuario, u.nome AS nome_usuario
    #        FROM LISTAS_DE_TAREFAS l
    #        INNER JOIN USUARIOS u ON l.Id_Usuario = u.Id_Usuario
    #        WHERE l.Id_Lista = %s''',
    #     (id_lista,)
    # ).fetchone()

    cursor.execute(
          '''SELECT l.Id_Lista, l.nome, l.Id_Usuario, u.nome AS nome_usuario
            FROM LISTAS_DE_TAREFAS l
           INNER JOIN USUARIOS u ON l.Id_Usuario = u.Id_Usuario
           WHERE l.Id_Lista = %s''',
           (id_lista,)
    ) 
    lista = cursor.fetchone()  # Obtém a lista de tarefas pelo ID, juntando com a tabela de usuários para obter informações do usuário associado.

    if lista is None:
        abort(404, f"Lista id {id_lista} não existe.")

    if check_author and lista['Id_Usuario'] != g.user['Id_Usuario']:
        abort(403)

    return lista

# verifica se a tarefa existe e se o usuário é o autor da tarefa, caso contrário, retorna um erro 404 ou 403.
def get_tarefa(id_tarefa, check_author=True):
    cursor = get_cursor()
    # tarefa = get_db().execute(
    #     '''SELECT t.id_tarefa, t.descricao, t.concluida, t.data_criacao, t.data_conclusao, t.Id_lista, l.Id_Usuario
    #        FROM TAREFAS t
    #        INNER JOIN LISTAS_DE_TAREFAS l ON t.Id_lista = l.Id_lista
    #        WHERE t.id_tarefa = %s''',
    #     (id_tarefa,)
    # ).fetchone()

    cursor.execute(
        '''SELECT t.id_tarefa, t.descricao, t.concluida, t.data_criacao, t.data_conclusao, t.Id_lista, l.Id_Usuario
           FROM TAREFAS t
           INNER JOIN LISTAS_DE_TAREFAS l ON t.Id_lista = l.Id_lista
           WHERE t.id_tarefa = %s''',
        (id_tarefa,)
    )
    tarefa = cursor.fetchone()  # Obtém a tarefa pelo ID, juntando com a tabela de listas de tarefas para obter informações da lista associada.

    if tarefa is None:
        abort(404, f"Tarefa id {id_tarefa} não existe.")

    if check_author and tarefa['Id_Usuario'] != g.user['Id_Usuario']:
        abort(403)

    return tarefa