import psycopg2

try:
    conn = psycopg2.connect(
        host="dpg-d3i65ore5dus738rvqj0-a.oregon-postgres.render.com",
        database="financeiro_db_3egf",
        user="financeiro_db_3egf_user",
        password="B1xUwbejZLJzciefomgyKiyBWJ95fuN3"
    )
    print("✅ Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print("❌ Erro ao conectar:", e)
