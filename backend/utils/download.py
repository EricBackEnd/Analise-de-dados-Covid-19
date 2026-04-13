"""
Utilitário para download e cache do CSV do Our World in Data.
"""

import logging
from datetime import datetime
from pathlib import Path
import requests

from backend.config.settings import ETLConfig

logger = logging.getLogger(__name__)


def download_csv():
    """
    Baixa CSV do Our World in Data e salva em cache local.
    
    Returns:
        Path: Caminho do arquivo CSV em cache
    """
    ETLConfig.CACHE_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    cache_file = ETLConfig.CACHE_DIR / f'owid-covid-data_{today}.csv'
    
    # Verifica se já existe cache do dia
    if cache_file.exists():
        logger.info(f"✓ Usando cache existente: {cache_file}")
        return cache_file
    
    # Baixa novo arquivo
    logger.info(f"⬇ Baixando CSV de {ETLConfig.CSV_URL}")
    try:
        response = requests.get(ETLConfig.CSV_URL, timeout=60)
        response.raise_for_status()
        
        with open(cache_file, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✓ CSV salvo em: {cache_file}")
        return cache_file
    
    except requests.RequestException as e:
        logger.error(f"❌ Erro ao baixar CSV: {e}")
        raise
