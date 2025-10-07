import psycopg2
import psycopg2.extras

try:
    conn = psycopg2.connect(
        host="dpg-d3i65ore5dus738rvqj0-a.oregon-postgres.render.com",
        database="financeiro_db_3egf",
        user="financeiro_db_3egf_user",
        password="B1xUwbejZLJzciefomgyKiyBWJ95fuN3",
        sslmode="require"
    )

    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT NOW();")  # comando simples
    resultado = cursor.fetchone()
    print("✅ Conexão OK! Horário do servidor:", resultado["now"])

    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Erro ao conectar:", e)
