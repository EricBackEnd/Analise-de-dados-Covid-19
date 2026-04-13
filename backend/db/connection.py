import psycopg2
from contextlib import contextmanager
import logging
from backend.config.settings import DatabaseConfig

logger = logging.getLogger(__name__)


def get_connection():
    """Cria e retorna uma conexão com o PostgreSQL."""
    try:
        conn = psycopg2.connect(**DatabaseConfig.get_connection_params())
        logger.info("✓ Conexão com PostgreSQL estabelecida")
        return conn
    except psycopg2.Error as e:
        logger.error(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        raise


def close_connection(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()
        logger.info("✓ Conexão com PostgreSQL fechada")


@contextmanager
def get_db_connection():
    """Context manager para gerenciar conexão automaticamente."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro na transação: {e}")
        raise
    finally:
        close_connection(conn)
