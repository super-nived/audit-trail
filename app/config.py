from dotenv import load_dotenv
import os

load_dotenv()


"""
Database Configuration
"""
DB_CONFIG ={
    "server": "iapps-in-dev-sql-server.database.windows.net",
    "port": 1433,
    "database": "IA_SFS_OCCDUBAII",
    "username": "iappsadmin",
    "password": "1@PpZd3vK0ch!#"
}
# JWT Public Key
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")
if not JWT_PUBLIC_KEY:
    raise ValueError("JWT_PUBLIC_KEY not found in environment variables.")
