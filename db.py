# ============================================================
# CONEXIÓN A POSTGRESQL
# ============================================================

import psycopg2
from config import DB_CONFIG

def get_connection():
    """Retorna una conexión activa a PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def test_connection():
    """Prueba que la conexión funcione correctamente."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conexión exitosa a PostgreSQL")
        print(f"   Versión: {version[0]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()
    