import sqlite3

conn = sqlite3.connect("banco.db")
cursor = conn.cursor()

# Tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
);
""")

# Tabela de transações
cursor.execute("""
CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    valor REAL NOT NULL,
    tipo TEXT CHECK(tipo IN ('entrada', 'saida')) NOT NULL,
    data TEXT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
""")

conn.commit()
conn.close()

print("✅ Banco de dados criado ou atualizado com sucesso!")
