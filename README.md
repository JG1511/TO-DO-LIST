# To-Do List Flask

Um projeto de lista de tarefas (To-Do List) feito com **Flask**, **SQLite** e **Bootstrap**.  
Permite múltiplos usuários, cada um com suas próprias listas e tarefas.

---

## Funcionalidades

- Cadastro e login de usuários
- Logout seguro
- Criação, edição e exclusão de listas de tarefas
- Criação, edição e exclusão de tarefas dentro de cada lista
- Marcação de tarefas como concluídas
- Interface responsiva com Bootstrap

---

## Estrutura do Banco de Dados

- **USUARIOS**: Id_Usuario, nome, email, senha
- **LISTAS_DE_TAREFAS**: Id_Lista, nome, Id_Usuario
- **TAREFAS**: id_tarefa, descricao, concluida, data_criacao, data_conclusao, Id_lista

---

## Como rodar o projeto

1. **Clone o repositório**
    ```sh
    git clone https://github.com/seu-usuario/to-do-list-flask.git
    cd to-do-list-flask
    ```

2. **Crie e ative um ambiente virtual**
    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. **Instale as dependências**
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure o banco de dados**
    ```sh
    flask --app main init-db
    ```

5. **Execute o servidor**
    ```sh
    flask --app main run
    ```

6. **Acesse em**  
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Estrutura de Pastas

```
main/
  ├── auth.py
  ├── db.py
  ├── list.py
  ├── templates/
  │     ├── base.html
  │     ├── auth/
  │     │     ├── login.html
  │     │     └── registro.html
  │     └── list/
  │           ├── index.html
  │           ├── criar.html
  │           ├── editar_lista.html
  │           ├── tarefas.html
  │           ├── criar_tarefa.html
  │           └── editar_tarefa.html
  └── static/
        └── style.css
```

---

## Observações

- O projeto usa Flask Blueprints para separar autenticação e listas/tarefas.
- O campo `g.user` é usado para acessar o usuário logado.
- O banco de dados é SQLite e pode ser inicializado com o script `tables.sql`.

---

## Licença

MIT

---