import os
import psycopg2

# Conecta ao banco do Render via variável de ambiente
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("❌ ERRO: Variável DATABASE_URL não encontrada!")
    conn = psycopg2.connect(db_url, sslmode="require")
    return conn

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Criação da tabela de usuários
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Criação da tabela de transações
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
