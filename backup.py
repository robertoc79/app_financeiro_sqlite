import psycopg2
import csv
from datetime import datetime
from flask import Blueprint, send_file, session, redirect, url_for, flash, make_response
from io import StringIO

backup_bp = Blueprint("backup", __name__)

def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-d3i99ojipnbc73e02mgg-a.oregon-postgres.render.com",
        database="financeiro_db_df54",
        user="financeiro_db_df54_user",
        password="nJOczlaGBRni7mFw5SbnF6jD9l9ejonU",
        sslmode="require"
    )
    return conn


@backup_bp.route("/backup")
def gerar_backup():
    if "usuario_id" not in session:
        flash("Faça login para gerar o backup.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT descricao, valor, tipo, data
        FROM transacoes
        WHERE usuario_id = %s
        ORDER BY data DESC
    """, (session["usuario_id"],))
    rows = cur.fetchall()

    if not rows:
        flash("Nenhuma transação encontrada para backup.", "info")
        cur.close()
        conn.close()
        return redirect(url_for("dashboard"))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Descrição", "Valor", "Tipo", "Data"])
    writer.writerows(rows)
    output.seek(0)

    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"

    cur.close()
    conn.close()
    flash("✅ Backup gerado com sucesso!", "success")

    return response
