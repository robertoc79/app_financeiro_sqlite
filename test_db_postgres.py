import psycopg2

# --- Conexão com o banco PostgreSQL (Render) ---
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="dpg-d3i99ojipnbc73e02mgg-a.oregon-postgres.render.com",
            dbname="financeiro_db_df54",
            user="financeiro_db_df54_user",
            password="nJOczlaGBRni7mFw5SbnF6jD9l9ejonU",
            sslmode="require"
        )
        print("✅ Conexão bem-sucedida com o banco PostgreSQL (Render)!")
        return conn
    except Exception as e:
        print("❌ Erro ao conectar:", e)
        return None


# --- Teste simples de conexão ---
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT version();")
        versao = cur.fetchone()
        print("🧠 Versão do PostgreSQL:", versao[0])
        cur.close()
        conn.close()
