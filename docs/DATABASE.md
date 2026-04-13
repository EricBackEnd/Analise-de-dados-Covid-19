# 🗄️ ESTRATÉGIA DE BANCO DE DADOS

## Arquitetura Híbrida (DuckDB + PostgreSQL)

```
CSV → DuckDB (processamento) → Pandas (redução) → PostgreSQL (persistência)
```

---

## Por que DuckDB?

**DuckDB** é um banco analítico embarcado (in-process) otimizado para análise de dados.

### Características

- **In-Process**: Roda dentro do Python, sem servidor separado
- **Analítico**: Otimizado para queries OLAP (agregações, análises)
- **Embarcado**: Como SQLite, mas para análise de dados
- **SQL Completo**: Suporta queries SQL complexas

### Vantagens

1. **Performance em CSV**
   - Processa arquivos grandes (500MB+) diretamente
   - Não precisa carregar tudo na memória
   - Leitura otimizada com filtros durante scan

2. **Eficiência de Memória**
   - Filtra dados durante leitura (não carrega tudo na RAM)
   - Streaming de dados
   - Compressão automática

3. **Velocidade**
   - 10-100x mais rápido que Pandas puro em agregações
   - Execução vetorizada
   - Paralelização automática

4. **Zero Configuração**
   - `pip install duckdb`
   - Não precisa de servidor separado
   - Não precisa de configuração

5. **SQL Analítico**
   - Window functions
   - CTEs (Common Table Expressions)
   - Agregações complexas
   - JOINs eficientes

### Exemplo de Eficiência

```python
# ❌ Pandas puro (lento, usa muita RAM)
df = pd.read_csv('huge.csv')  # Carrega TUDO na memória (5GB)
df = df[df['country'].isin(countries)]  # Filtra DEPOIS de carregar
df = df[df['date'] >= '2020-01-01']  # Mais filtros DEPOIS
# Resultado: 5GB de RAM usados, 30 segundos

# ✅ DuckDB (rápido, eficiente)
query = """
    SELECT * FROM 'huge.csv' 
    WHERE country IN ('Brazil', 'USA', 'India')
      AND date >= '2020-01-01'
"""
df = duckdb.query(query).df()  # Filtra DURANTE leitura
# Resultado: 500MB de RAM usados, 3 segundos
```

### Quando Usar DuckDB

✅ **Use DuckDB para:**
- Ler e processar CSVs grandes
- Agregações complexas
- Filtros durante leitura
- Transformações ETL
- Análises exploratórias

❌ **NÃO use DuckDB para:**
- Persistência de dados (use PostgreSQL)
- Aplicações transacionais (OLTP)
- Múltiplos usuários simultâneos
- Dados que precisam de ACID completo

---

## Por que PostgreSQL?

**PostgreSQL** é um banco de dados relacional robusto e escalável.

### Vantagens

1. **Persistência Confiável**
   - Dados estruturados e indexados
   - Durabilidade garantida
   - Backup e recovery

2. **Queries Complexas**
   - JOINs eficientes
   - Agregações temporais
   - Window functions
   - CTEs recursivas

3. **Integridade**
   - ACID completo (Atomicity, Consistency, Isolation, Durability)
   - Constraints (PK, FK, CHECK, UNIQUE)
   - Transações
   - Rollback

4. **Produção**
   - Escalável (milhões de registros)
   - Robusto e testado
   - Suporte a índices (B-tree, Hash, GiST, GIN)
   - Otimizador de queries avançado

5. **Ecossistema**
   - Ferramentas de administração (pgAdmin, DBeaver)
   - Extensões (PostGIS, TimescaleDB)
   - Integração com ORMs
   - Comunidade ativa

### Quando Usar PostgreSQL

✅ **Use PostgreSQL para:**
- Persistência de dados processados
- Queries de aplicação (API)
- Dados que precisam de integridade
- Múltiplos usuários simultâneos
- Produção

---

## Pipeline Completo

### Etapa 1: Extração
```
CSV (500MB) → Download/Cache
```

### Etapa 2: Transformação (DuckDB)
```python
# DuckDB processa CSV diretamente
query = """
    SELECT 
        location as country,
        date,
        COALESCE(total_cases, 0) as total_cases,
        ...
    FROM 'owid-covid-data.csv'
    WHERE location IN ('Brazil', 'USA', ...)
      AND date BETWEEN '2020-01-01' AND '2023-12-31'
    ORDER BY location, date
"""
df = duckdb.query(query).df()
# Resultado: DataFrame Pandas com ~50k registros
```

### Etapa 3: Redução (Pandas)
```python
# Pandas converte tipos para PostgreSQL
df['date'] = pd.to_datetime(df['date']).dt.date
df['total_cases'] = df['total_cases'].astype('Int64').astype(object)
# Resultado: DataFrame otimizado para inserção
```

### Etapa 4: Carga (PostgreSQL)
```python
# PostgreSQL persiste dados
cursor.executemany(insert_query, df.values.tolist())
conn.commit()
# Resultado: 50k registros no banco
```

---

## Comparação

| Aspecto | DuckDB | PostgreSQL |
|---------|--------|------------|
| **Tipo** | Analítico (OLAP) | Transacional (OLTP) |
| **Uso** | Processamento ETL | Persistência |
| **Performance** | Leitura/Agregação | Escrita/Consulta |
| **Configuração** | Zero | Servidor |
| **Concorrência** | Single-user | Multi-user |
| **Persistência** | Temporária | Permanente |
| **ACID** | Limitado | Completo |

---

## Decisão Arquitetural

**Por que não usar apenas PostgreSQL?**
- PostgreSQL não lê CSV diretamente de forma eficiente
- Carregar 500MB de CSV no PostgreSQL é lento
- DuckDB é 10-100x mais rápido para processar CSV

**Por que não usar apenas DuckDB?**
- DuckDB não é ideal para persistência
- PostgreSQL é melhor para queries de aplicação
- PostgreSQL tem melhor suporte a múltiplos usuários

**Solução híbrida:**
- DuckDB para ETL (força dele)
- PostgreSQL para API (força dele)
- Cada ferramenta no que faz melhor
