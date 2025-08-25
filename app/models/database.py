import sqlite3

DATABASE = "veterinaria.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
    return conn
