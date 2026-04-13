"""
Repositório para operações de banco de dados da tabela covid_data.
Utiliza SQL puro com psycopg2.
"""

import logging
from backend.model.covid_model import CREATE_TABLE_SQL, CREATE_INDEXES_SQL

logger = logging.getLogger(__name__)


def create_table(conn):
    """Cria tabela covid_data e índices no PostgreSQL."""
    try:
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(CREATE_INDEXES_SQL)
        conn.commit()
        cursor.close()
        logger.info("✓ Tabela covid_data e índices criados")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabela: {e}")
        raise


def truncate_table(conn):
    """Remove todos os registros da tabela covid_data."""
    try:
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE covid_data RESTART IDENTITY CASCADE")
        conn.commit()
        cursor.close()
        logger.info("✓ Tabela covid_data truncada")
    except Exception as e:
        logger.error(f"❌ Erro ao truncar tabela: {e}")
        raise


def bulk_insert(conn, df):
    """
    Insere dados em lote na tabela covid_data.
    
    Args:
        conn: Conexão psycopg2
        df: DataFrame pandas com os dados
    """
    try:
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO covid_data 
        (country, date, total_cases, new_cases, total_deaths, 
         new_deaths, total_vaccinations, people_vaccinated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Converte DataFrame para lista de tuplas
        records = df.to_records(index=False)
        data = [tuple(row) for row in records]
        
        # Executa insert em batch
        cursor.executemany(insert_query, data)
        conn.commit()
        cursor.close()
        
        logger.info(f"✓ {len(df)} registros inseridos na tabela covid_data")
        return len(df)
    
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro ao inserir dados: {e}")
        raise


def get_all_countries(conn):
    """Retorna lista de todos os países na tabela."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT country FROM covid_data ORDER BY country")
        countries = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return countries
    except Exception as e:
        logger.error(f"❌ Erro ao buscar países: {e}")
        raise


def get_record_count(conn):
    """Retorna total de registros na tabela."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM covid_data")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Exception as e:
        logger.error(f"❌ Erro ao contar registros: {e}")
        raise
