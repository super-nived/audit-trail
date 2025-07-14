import pymssql
from app.config import DB_CONFIG

def get_db_connection():
    """Establishes a connection to the database."""
    return pymssql.connect(
        server=DB_CONFIG['server'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['username'],
        password=DB_CONFIG['password']
    )
