import os
from pathlib import Path

# BASE_DIR pode ter acentos no caminho, causando erro no Windows
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Tenta carregar .env, mas ignora erros de encoding
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.ENV')
except:
    pass


class DatabaseConfig:
    """Configurações do banco de dados PostgreSQL."""
    
    DB_NAME = os.getenv('db_name', 'covidanalise').strip()
    DB_USER = os.getenv('db_user', 'postgres').strip()
    DB_PASSWORD = os.getenv('db_password', 'postgres').strip()
    DB_HOST = os.getenv('db_host', 'localhost').strip()
    DB_PORT = os.getenv('db_port', '5432').strip()
    
    @classmethod
    def get_connection_params(cls):
        """Retorna dicionário com parâmetros de conexão."""
        return {
            'dbname': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'host': cls.DB_HOST,
            'port': cls.DB_PORT
        }


class ETLConfig:
    """Configurações do pipeline ETL."""
    
    CSV_URL = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    CACHE_DIR = BASE_DIR / 'cache'
    DATE_START = '2020-01-01'
    DATE_END = '2023-12-31'
    
    PRIORITY_COUNTRIES = [
        'China', 'India', 'United States', 'Indonesia', 'Pakistan',
        'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico',
        'Japan', 'Philippines', 'Egypt', 'Vietnam', 'Germany',
        'United Kingdom', 'France', 'Italy', 'Spain', 'Turkey',
        'Argentina', 'Colombia', 'Iran', 'South Africa', 'Canada',
        'Peru', 'Chile', 'Netherlands', 'Belgium', 'Sweden',
        'World', 'Europe', 'Asia', 'North America', 'South America', 
        'Africa', 'Oceania'
    ]
