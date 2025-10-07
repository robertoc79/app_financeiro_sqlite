import psycopg2

# --- Conexão com o banco PostgreSQL (Render) ---
def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-d3i65ore5dus738rvqj0-a.oregon-postgres.render.com",
        database="financeiro_db_3egf",
        user="financeiro_db_3egf_user",
        password="B1xUwbejZLJzciefomgyKiyBWJ95fuN3",
        sslmode="require"
    )
    return conn

# --- Criação das tabelas ---
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id SERIAL PRIMARY KEY,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        descricao VARCHAR(255) NOT NULL,
        valor NUMERIC(10,2) NOT NULL,
        tipo VARCHAR(10) CHECK (tipo IN ('entrada', 'saida')) NOT NULL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabelas criadas com sucesso no PostgreSQL!")

if __name__ == "__main__":
    create_tables()
