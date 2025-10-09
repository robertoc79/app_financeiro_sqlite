from flask import Flask, render_template, request, redirect, session, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

from backup import backup_bp  # importa o blueprint

app = Flask(__name__)
app.secret_key = "chave_segura"

app.register_blueprint(backup_bp)  # registra o blueprint DEPOIS


# --- Conexão com PostgreSQL (Render) ---
def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-d3i99ojipnbc73e02mgg-a.oregon-postgres.render.com",
        database="financeiro_db_df54",
        user="financeiro_db_df54_user",
        password="nJOczlaGBRni7mFw5SbnF6jD9l9ejonU",
        sslmode="require"
    )
    return conn


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
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            flash("E-mail já cadastrado. Faça login.", "warning")
            cur.close()
            conn.close()
            return redirect(url_for('login'))

        cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
                    (nome, email, senha_hash))
        conn.commit()
        cur.close()
        conn.close()

        flash("Usuário cadastrado com sucesso!", "success")
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
            session['usuario_nome'] = user['nome']
            return redirect(url_for('dashboard'))
        else:
            flash("Usuário ou senha incorretos!", "danger")

    return render_template('login.html')


# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Pega todas as transações do usuário
    cur.execute("SELECT * FROM transacoes WHERE usuario_id=%s ORDER BY data DESC", (session['usuario_id'],))
    transacoes = cur.fetchall()

    # Calcula total de entradas, saídas e saldo
    entradas_total = sum([t['valor'] for t in transacoes if t['tipo'] == 'entrada'])
    saidas_total = sum([t['valor'] for t in transacoes if t['tipo'] == 'saida'])
    saldo = entradas_total - saidas_total

    cur.close()
    conn.close()

    return render_template(
        'dashboard.html',
        transacoes=transacoes,
        saldo=saldo,
        entradas_total=entradas_total,
        saidas_total=saidas_total,
        usuario=session.get('usuario_nome')
    )



# --- Adicionar transação ---
@app.route('/add_transacao', methods=['POST'])
def add_transacao():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    descricao = request.form['descricao']
    valor = request.form['valor']
    tipo = request.form['tipo']

    if not valor.replace('.', '', 1).isdigit():
        flash("O valor deve ser numérico.", "danger")
        return redirect(url_for('dashboard'))

    valor = float(valor)
    if valor <= 0:
        flash("O valor deve ser maior que zero.", "danger")
        return redirect(url_for('dashboard'))

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

    flash("Transação adicionada com sucesso!", "success")
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
        flash("Transação atualizada!", "info")
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

    flash("Transação excluída!", "danger")
    return redirect(url_for('dashboard'))


# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
