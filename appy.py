from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_segura"

# --- Conexão com PostgreSQL (Render) ---
def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-d3i65ore5dus738rvqj0-a.oregon-postgres.render.com",
        database="financeiro_db_3egf",
        user="financeiro_db_3egf_user",
        password="B1xUwbejZLJzciefomgyKiyBWJ95fuN3",
        sslmode="require"
    )
    return conn


# --- Rota principal ---
@app.route('/')
def index():
    return redirect(url_for('login'))


# --- Cadastro de usuário ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        senha_hash = generate_password_hash(senha)

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha_hash))
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return "E-mail já cadastrado!"
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')


# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user['senha'], senha):
            session['usuario_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return "Usuário ou senha incorretos!"
    return render_template('login.html')


# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM transacoes WHERE usuario_id=%s ORDER BY data DESC", (session['usuario_id'],))
    transacoes = cur.fetchall()

    saldo = sum([t['valor'] if t['tipo'] == 'entrada' else -t['valor'] for t in transacoes])

    cur.close()
    conn.close()

    return render_template('dashboard.html', transacoes=transacoes, saldo=saldo)


# --- Adicionar transação ---
@app.route('/add_transacao', methods=['POST'])
def add_transacao():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    descricao = request.form['descricao']
    valor = float(request.form['valor'])
    tipo = request.form['tipo']
    data = datetime.now()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transacoes (usuario_id, descricao, valor, tipo, data) VALUES (%s, %s, %s, %s, %s)",
        (session['usuario_id'], descricao, valor, tipo, data)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('dashboard'))


# --- Editar transação ---
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == 'POST':
        descricao = request.form['descricao']
        valor = float(request.form['valor'])
        tipo = request.form['tipo']
        data = request.form['data']

        cur.execute("""
            UPDATE transacoes SET descricao=%s, valor=%s, tipo=%s, data=%s 
            WHERE id=%s AND usuario_id=%s
        """, (descricao, valor, tipo, data, id, session['usuario_id']))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM transacoes WHERE id=%s AND usuario_id=%s", (id, session['usuario_id']))
    transacao = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('editar.html', transacao=transacao)


# --- Excluir transação ---
@app.route('/excluir/<int:id>')
def excluir(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM transacoes WHERE id=%s AND usuario_id=%s", (id, session['usuario_id']))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('dashboard'))


# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
