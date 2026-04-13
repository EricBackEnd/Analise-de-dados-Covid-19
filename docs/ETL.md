# 🔄 PIPELINE ETL

## Visão Geral

```
Extração → Transformação → Carga
   ↓            ↓            ↓
  CSV       DuckDB      PostgreSQL
```

---

## ETAPA 1 — EXTRAÇÃO

### Objetivo
Obter dados atualizados da fonte oficial.

### Fonte de Dados
- **URL**: `https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv`
- **Organização**: Our World in Data (OWID)
- **Atualização**: Diária (dados históricos completos)
- **Tamanho**: ~500MB

### Implementação

**Arquivo**: `backend/utils/download.py`

**Funcionalidades**:
1. Download automático do CSV
2. Cache local para evitar downloads repetidos
3. Verificação de data (reutilizar cache do mesmo dia)
4. Tratamento de erros de rede

**Fluxo**:
```python
1. Verificar se existe cache do dia atual
2. Se existe → usar cache
3. Se não existe → baixar CSV
4. Salvar em cache/owid-covid-data_YYYY-MM-DD.csv
5. Retornar caminho do arquivo
```

**Cache**:
- Diretório: `cache/`
- Formato: `owid-covid-data_YYYY-MM-DD.csv`
- Benefício: Evita downloads repetidos durante desenvolvimento

---

## ETAPA 2 — TRANSFORMAÇÃO

### Objetivo
Processar e filtrar dados usando DuckDB para máxima eficiência.

### Implementação

**Arquivo**: `backend/services/etl_service.py`

### 2.1 - Filtros Aplicados

**Países/Regiões (37 entidades)**:
```python
PRIORITY_COUNTRIES = [
    # 30 países mais populosos
    'China', 'India', 'United States', 'Indonesia', 'Pakistan',
    'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico',
    'Japan', 'Philippines', 'Egypt', 'Vietnam', 'Germany',
    'United Kingdom', 'France', 'Italy', 'Spain', 'Turkey',
    'Argentina', 'Colombia', 'Iran', 'South Africa', 'Canada',
    'Peru', 'Chile', 'Netherlands', 'Belgium', 'Sweden',
    
    # 7 agregações continentais/globais
    'World', 'Europe', 'Asia', 'North America', 
    'South America', 'Africa', 'Oceania'
]
```

**Período**:
- Início: `2020-01-01` (primeiros casos)
- Fim: `2023-12-31` (pós-vacinação)
- Justificativa: Captura início, pico e fase de vacinação

### 2.2 - Colunas Selecionadas

```sql
SELECT 
    location as country,           -- Renomeia para clareza
    date,                          -- Data do registro
    COALESCE(total_cases, 0),      -- Total acumulado de casos
    COALESCE(new_cases, 0),        -- Novos casos no dia
    COALESCE(total_deaths, 0),     -- Total acumulado de mortes
    COALESCE(new_deaths, 0),       -- Novas mortes no dia
    COALESCE(total_vaccinations, 0), -- Total de doses aplicadas
    COALESCE(people_vaccinated, 0)   -- Pessoas vacinadas (1+ dose)
FROM 'owid-covid-data.csv'
WHERE ...
```

**Justificativa das colunas**:
- `total_cases/deaths`: Análise de evolução acumulada
- `new_cases/deaths`: Análise de tendências diárias
- `total_vaccinations`: Cobertura vacinal
- `people_vaccinated`: Pessoas com pelo menos 1 dose

### 2.3 - Tratamento de Dados

**Valores Nulos**:
```sql
COALESCE(column, 0)  -- Substitui NULL por 0
```

**Justificativa**:
- Dados ausentes = sem registro naquele dia
- Zero é mais apropriado que NULL para análises numéricas
- Facilita agregações e cálculos

**Conversão de Tipos**:
```python
# Data: numpy.datetime64 → datetime.date (Python nativo)
df['date'] = pd.to_datetime(df['date']).dt.date

# Números: numpy.int64 → int (Python nativo)
numeric_cols = ['total_cases', 'new_cases', 'total_deaths', 
                'new_deaths', 'total_vaccinations', 'people_vaccinated']
for col in numeric_cols:
    df[col] = df[col].astype('Int64').astype(object)
```

**Justificativa**:
- psycopg2 não aceita tipos numpy
- Tipos Python nativos são compatíveis com PostgreSQL
- Evita erros de adaptação de tipos

**Ordenação**:
```sql
ORDER BY location, date
```

**Justificativa**:
- Facilita análises temporais
- Melhora performance de queries subsequentes
- Dados organizados logicamente

### 2.4 - Query DuckDB Completa

```python
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
      AND date >= '{DATE_START}'
      AND date <= '{DATE_END}'
    ORDER BY location, date
"""

conn = duckdb.connect(':memory:')
df = conn.execute(query).df()
conn.close()
```

**Resultado**:
- ~53.917 registros (37 países × ~1.461 dias)
- DataFrame Pandas otimizado
- Pronto para carga no PostgreSQL

---

## ETAPA 3 — CARGA

### Objetivo
Persistir dados transformados no PostgreSQL.

### Implementação

**Arquivo**: `backend/repositories/covid_repository.py`

### 3.1 - Estrutura da Tabela

```sql
CREATE TABLE IF NOT EXISTS covid_data (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    total_cases BIGINT DEFAULT 0,
    new_cases BIGINT DEFAULT 0,
    total_deaths BIGINT DEFAULT 0,
    new_deaths BIGINT DEFAULT 0,
    total_vaccinations BIGINT DEFAULT 0,
    people_vaccinated BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country, date)
);
```

**Índices**:
```sql
CREATE INDEX IF NOT EXISTS idx_country ON covid_data(country);
CREATE INDEX IF NOT EXISTS idx_date ON covid_data(date);
CREATE INDEX IF NOT EXISTS idx_country_date ON covid_data(country, date);
```

**Justificativa**:
- `idx_country`: Queries por país
- `idx_date`: Queries por período
- `idx_country_date`: Queries combinadas (mais comum)
- UNIQUE(country, date): Evita duplicação

### 3.2 - Estratégia de Carga

**Opção escolhida**: TRUNCATE + INSERT

```python
# 1. Truncar tabela (remover todos os dados)
TRUNCATE TABLE covid_data;

# 2. Inserir todos os dados novamente
INSERT INTO covid_data (country, date, total_cases, ...)
VALUES (%s, %s, %s, ...);
```

**Justificativa**:
- Dados históricos completos (não incrementais)
- Evita complexidade de UPSERT
- Mais rápido para carga completa
- Simples e direto

**Alternativa (não usada)**: UPSERT
```sql
INSERT INTO covid_data (...)
VALUES (...)
ON CONFLICT (country, date) 
DO UPDATE SET ...;
```
- Mais complexo
- Mais lento para carga completa
- Útil apenas para atualizações incrementais

### 3.3 - Inserção em Lote

```python
cursor.executemany(insert_query, data)
conn.commit()
```

**Justificativa**:
- `executemany` é mais rápido que múltiplos `execute`
- Insere ~53k registros em ~4 segundos
- Uma única transação (atomicidade)

---

## Execução do Pipeline

### Script Principal

**Arquivo**: `load_data.py`

```python
def main():
    # 1. Extração
    csv_path = extract_data()
    
    # 2. Transformação
    df = transform_data(csv_path)
    
    # 3. Carga
    load_data(df)
    
    # 4. Estatísticas
    return stats
```

### Logs

```
🚀 Iniciando pipeline ETL COVID-19
📥 Iniciando extração de dados
✓ Usando cache existente: cache/owid-covid-data_2026-04-13.csv
🔄 Iniciando transformação com DuckDB
✓ Transformação concluída: 53917 registros
✓ Período: 2020-01-01 a 2023-12-31
✓ Países: 37
📤 Iniciando carga no PostgreSQL
✓ Conexão com PostgreSQL estabelecida
✓ Tabela covid_data e índices criados
✓ Tabela covid_data truncada
✓ 53917 registros inseridos na tabela covid_data
✓ Carga concluída com sucesso
✓ Conexão com PostgreSQL fechada
✅ ETL concluído com sucesso!
```

### Resultado Esperado

```
==================================================
ETL CONCLUIDO COM SUCESSO!
==================================================
Total de registros: 53,917
Paises carregados: 37
Periodo: 2020-01-01 a 2023-12-31
==================================================
```

---

## Performance

### Métricas

- **Extração**: ~2 segundos (com cache) / ~30 segundos (download)
- **Transformação**: ~0.3 segundos (DuckDB)
- **Carga**: ~4 segundos (PostgreSQL)
- **Total**: ~6 segundos (com cache)

### Otimizações Aplicadas

1. **Cache de CSV**: Evita downloads repetidos
2. **DuckDB**: Filtra durante leitura (não carrega tudo)
3. **Bulk insert**: executemany ao invés de múltiplos execute
4. **Índices**: Criados após inserção (mais rápido)
5. **Transação única**: Commit uma vez ao final

---

## Tratamento de Erros

### Extração
- Timeout de rede → Retry
- Arquivo corrompido → Re-download
- Sem espaço em disco → Erro claro

### Transformação
- CSV inválido → Erro descritivo
- Colunas faltando → Erro claro
- Tipos incompatíveis → Conversão ou erro

### Carga
- Conexão perdida → Rollback
- Constraint violation → Rollback
- Erro de inserção → Rollback + log

---

## Manutenção

### Atualizar Dados
```bash
python load_data.py
```

### Limpar Cache
```bash
rm -rf cache/*
```

### Recriar Tabela
```sql
DROP TABLE covid_data;
-- Executar load_data.py novamente
```
