"""Script executor do pipeline ETL COVID-19."""

import logging
from backend.services.etl_service import run_etl

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Executa pipeline ETL."""
    try:
        stats = run_etl()
        
        print("\n" + "="*50)
        print("ETL CONCLUIDO COM SUCESSO!")
        print("="*50)
        print(f"Total de registros: {stats['total_records']:,}")
        print(f"Paises carregados: {stats['countries']}")
        print(f"Periodo: {stats['date_start']} a {stats['date_end']}")
        print("="*50 + "\n")
    
    except Exception as e:
        logger.error(f"Falha no ETL: {e}")
        raise


if __name__ == '__main__':
    main()
