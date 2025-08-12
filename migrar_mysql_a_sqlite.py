import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.types import Enum, String
from sqlalchemy.exc import OperationalError

# Configura tus conexiones
mysql_url = "mysql+pymysql://root:@localhost/veterinaria"
sqlite_path = "instance/flaskdb.sqlite"

# Elimina archivo sqlite anterior
if os.path.exists(sqlite_path):
    os.remove(sqlite_path)
    print("✅ Archivo SQLite eliminado para evitar conflictos.")

# Conexiones
mysql_engine = create_engine(mysql_url)
sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")

# Reflejar estructura MySQL
metadata = MetaData()
metadata.reflect(bind=mysql_engine)

# Convertir ENUMs a String
for table in metadata.tables.values():
    for column in table.columns:
        if isinstance(column.type, Enum):
            column.type = String(50)  # o String(20) si tus ENUMs son cortos

# Crear tablas en SQLite
try:
    metadata.create_all(bind=sqlite_engine)
    print("✅ Tablas creadas correctamente en SQLite.")
except OperationalError as e:
    print("❌ Error al crear tablas:", e)

# Copiar datos
with mysql_engine.connect() as mysql_conn, sqlite_engine.begin() as sqlite_conn:
    for table in metadata.sorted_tables:
        print(f"Copiando tabla: {table.name}")
        data = mysql_conn.execute(table.select()).fetchall()
        if data:
            sqlite_conn.execute(table.insert(), data)

print("✅ Migración completada con éxito.")
