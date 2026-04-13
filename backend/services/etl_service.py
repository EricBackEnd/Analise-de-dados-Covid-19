"""
Serviço ETL para processamento de dados COVID-19.
Orquestra extração, transformação e carga.
"""

import logging
import pandas as pd
import duckdb

from backend.config.settings import ETLConfig
from backend.utils.download import download_csv
from backend.db.connection import get_connection, close_connection
from backend.repositories import covid_repository

logger = logging.getLogger(__name__)


def extract_data():
    """
    Extrai dados do CSV (download ou cache).
    
    Returns:
        Path: Caminho do arquivo CSV
    """
    logger.info("📥 Iniciando extração de dados")
    csv_path = download_csv()
    return csv_path


def transform_data(csv_path):
    """
    Transforma dados usando DuckDB para queries analíticas otimizadas.
    
    Args:
        csv_path: Caminho do arquivo CSV
        
    Returns:
        DataFrame: Dados transformados
    """
    logger.info("🔄 Iniciando transformação com DuckDB")
    
    # Cria lista de países para query SQL
    countries_list = "', '".join(ETLConfig.PRIORITY_COUNTRIES)
    
    # Query SQL otimizada no CSV
    query = f"""
    SELECT 
        location as country,
        date,
        COALESCE(total_cases, 0) as total_cases,
        COALESCE(new_cases, 0) as new_cases,
        COALESCE(total_deaths, 0) as total_deaths,
        COALESCE(new_deaths, 0) as new_deaths,
        COALESCE(total_vaccinations, 0) as total_vaccinations,
        COALESCE(people_vaccinated, 0) as people_vaccinated
    FROM '{csv_path}'
    WHERE location IN ('{countries_list}')
      AND date >= '{ETLConfig.DATE_START}'
      AND date <= '{ETLConfig.DATE_END}'
    ORDER BY location, date
    """
    
    try:
        # Executa query com DuckDB
        conn = duckdb.connect(':memory:')
        df = conn.execute(query).df()
        conn.close()
        
        # Converte data para datetime.date (compatível com PostgreSQL)
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Converte colunas numéricas para tipos Python nativos
        numeric_cols = ['total_cases', 'new_cases', 'total_deaths', 'new_deaths', 
                        'total_vaccinations', 'people_vaccinated']
        for col in numeric_cols:
            df[col] = df[col].astype('Int64').astype(object)
        
        logger.info(f"✓ Transformação concluída: {len(df)} registros")
        logger.info(f"✓ Período: {df['date'].min()} a {df['date'].max()}")
        logger.info(f"✓ Países: {df['country'].nunique()}")
        
        return df
    
    except Exception as e:
        logger.error(f"❌ Erro na transformação: {e}")
        raise


def load_data(df):
    """
    Carrega dados no PostgreSQL.
    
    Args:
        df: DataFrame com dados transformados
    """
    logger.info("📤 Iniciando carga no PostgreSQL")
    
    conn = get_connection()
    
    try:
        # Cria tabela se não existir
        covid_repository.create_table(conn)
        
        # Trunca tabela
        covid_repository.truncate_table(conn)
        
        # Insere dados
        covid_repository.bulk_insert(conn, df)
        
        logger.info("✓ Carga concluída com sucesso")
    
    finally:
        close_connection(conn)


def run_etl():
    """
    Executa pipeline ETL completo.
    
    Returns:
        dict: Estatísticas da execução
    """
    logger.info("🚀 Iniciando pipeline ETL COVID-19")
    
    try:
        # Extração
        csv_path = extract_data()
        
        # Transformação
        df = transform_data(csv_path)
        
        # Carga
        load_data(df)
        
        # Estatísticas
        stats = {
            'total_records': len(df),
            'countries': df['country'].nunique(),
            'date_start': df['date'].min(),
            'date_end': df['date'].max()
        }
        
        logger.info("✅ ETL concluído com sucesso!")
        return stats
    
    except Exception as e:
        logger.error(f"❌ Falha no ETL: {e}")
        raise
