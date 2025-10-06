from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_segura"

# --- Conexão com o banco ---
def get_db_connection():
    conn = sqlite3.connect("banco.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- Rotas ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha)).fetchone()
        conn.close()

        if user:
            session['usuario_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return "Usuário ou senha incorretos!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    transacoes = conn.execute(
        "SELECT * FROM transacoes WHERE usuario_id=? ORDER BY data DESC",
        (session['usuario_id'],)
    ).fetchall()

    saldo = sum([t['valor'] if t['tipo'] == 'entrada' else -t['valor'] for t in transacoes])
    conn.close()

    return render_template('dashboard.html', transacoes=transacoes, saldo=saldo)

@app.route('/add_transacao', methods=['POST'])
def add_transacao():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    tipo = request.form['tipo']
    data = request.form['data'] if request.form['data'] else datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO transacoes (usuario_id, descricao, valor, tipo, data) VALUES (?, ?, ?, ?, ?)",
        (session['usuario_id'], descricao, valor, tipo, data)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# --- Editar transação ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    transacao = conn.execute(
        "SELECT * FROM transacoes WHERE id=? AND usuario_id=?",
        (id, session['usuario_id'])
    ).fetchone()

    if not transacao:
        conn.close()
        return "Transação não encontrada."

    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = float(request.form['valor'])
        tipo = request.form['tipo']
        data = request.form['data']

        conn.execute(
            "UPDATE transacoes SET descricao=?, valor=?, tipo=?, data=? WHERE id=? AND usuario_id=?",
            (descricao, valor, tipo, data, id, session['usuario_id'])
        )
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('editar.html', transacao=transacao)

# --- Excluir transação ---
@app.route('/excluir/<int:id>')
def excluir(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM transacoes WHERE id=? AND usuario_id=?", (id, session['usuario_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
