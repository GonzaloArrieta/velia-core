import os 
import psycopg
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno desde un archivo .env
DATABASE_URL = os.environ.get("DATABASE_URL") 

def get_conn():
    return psycopg.connect(DATABASE_URL)   

