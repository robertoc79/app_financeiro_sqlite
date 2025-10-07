import psycopg2

# Conexão com o banco PostgreSQL (Render)
conn = psycopg2.connect(
    host="dpg-d3i65ore5dus738rvqj0-a.oregon-postgres.render.com",
    database="financeiro_db_3egf",
    user="financeiro_db_3egf_user",
    password="B1xUwbejZLJzciefomgyKiyBWJ95fuN3",
    sslmode="require"
)

cur = conn.cursor()

# Criação das tabelas
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    tipo TEXT CHECK(tipo IN ('entrada', 'saida')),
    data TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
cur.close()
conn.close()

print("✅ Tabelas criadas com sucesso no PostgreSQL!")
