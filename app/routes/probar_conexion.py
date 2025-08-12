from flask import Blueprint, jsonify
import sqlite3
import os

conexion_bp = Blueprint('conexion_bp', __name__)

@conexion_bp.route('/probar-conexion')
def probar_conexion():
    try:
        # Ruta absoluta a la base de datos en instance/
        ruta_db = os.path.join(os.getcwd(), 'instance', 'flaskdb.sqlite')
        conn = sqlite3.connect(ruta_db)
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({"mensaje": "✅ Conexión a SQLite exitosa"})
    except Exception as e:
        return jsonify({"error": str(e)})
