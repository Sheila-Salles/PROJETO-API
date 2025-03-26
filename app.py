from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'database.db' # Define o nome do banco de dados

def get_db_connection():
    # Função para estabelecer a conexão com o banco de dados SQLite
    conn = sqlite3.connect(DATABASE)
    # Configura o retorno das linhas do banco de dados como dicionários
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Função para inicializar o banco de dados, criando a tabela 'livros' se não existir
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            autor TEXT NOT NULL,
            imagem_url TEXT NOT NULL
        )
    """)
    conn.commit() # Salva as alterações no banco de dados
    conn.close() # Fecha a conexão com o banco de dados
    print("Banco de dados inicializado com sucesso!!")

init_db() # Chama a função para inicializar o banco de dados

@app.route('/')
def homepage():
    # Rota para a página inicial, renderizando o template 'index.html'
    return render_template('index.html')

@app.route("/doar", methods=['POST'])
def doar():
    # Rota para cadastrar um novo livro (método POST)
    dados = request.get_json() # Obtém os dados do livro do corpo da requisição JSON
    titulo = dados.get("titulo")
    categoria = dados.get("categoria")
    autor = dados.get("autor")
    imagem_url = dados.get("imagem_url")

    # Verifica se todos os campos obrigatórios foram fornecidos
    if not all([titulo, categoria, autor, imagem_url]):
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

    try:
        # Tenta inserir o novo livro no banco de dados
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO livros (titulo, categoria, autor, imagem_url)
            VALUES (?, ?, ?, ?)
        """, (titulo, categoria, autor, imagem_url))
        conn.commit()
        conn.close()
        return jsonify({'mensagem': 'Livro cadastrado com sucesso'}), 201
    except sqlite3.Error as e:
        # Trata erros de banco de dados
        return jsonify({'erro': f'Erro no banco de dados: {e}'}), 500

@app.route('/livros', methods=['GET'])
def listar_livros():
    # Rota para listar todos os livros cadastrados (método GET)
    try:
        conn = get_db_connection()
        livros = conn.execute('SELECT * FROM livros').fetchall()
        conn.close()

        # Formata os resultados do banco de dados como uma lista de dicionários
        livros_formatados = [{
            'id': livro['id'],
            'titulo': livro['titulo'],
            'categoria': livro['categoria'],
            'autor': livro['autor'],
            'imagem_url': livro['imagem_url']
        } for livro in livros]

        return jsonify(livros_formatados)
    except sqlite3.Error as e:
        # Trata erros de banco de dados
        return jsonify({'erro': f'Erro no banco de dados: {e}'}), 500

@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    # Rota para deletar um livro pelo ID (método DELETE)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        conn.commit()
        conn.close()

        # Verifica se algum livro foi deletado
        if cursor.rowcount == 0:
            return jsonify({"erro": "Livro não encontrado"}), 404
        return jsonify({"mensagem": "Livro excluído com sucesso"}), 200
    except sqlite3.Error as e:
        # Trata erros de banco de dados
        return jsonify({'erro': f'Erro no banco de dados: {e}'}), 500

if __name__ == "__main__":
    app.run(debug=True) # Inicia o servidor Flask em modo de depuração