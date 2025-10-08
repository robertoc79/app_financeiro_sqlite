import os
import psycopg2

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("❌ ERRO: Variável DATABASE_URL não encontrada!")
    conn = psycopg2.connect(db_url, sslmode="require")
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # === TABELA DE USUÁRIOS ===
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # === TABELA DE TRANSAÇÕES ===
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

    # === TABELA DE BACKUPS (opcional) ===
    cur.execute("""
        CREATE TABLE IF NOT EXISTS backups (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            caminho_arquivo TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Todas as tabelas foram criadas ou já existem.")

if __name__ == "__main__":
    create_tables()
