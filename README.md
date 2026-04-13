# Analise-de-dados-Covid-19

## 📊 Pipeline ETL de Dados COVID-19

Projeto de análise de dados da pandemia COVID-19 utilizando dados públicos do **Our World in Data**.

---

## 🎯 OBJETIVO DO PROJETO

Aplicação de análise de dados COVID-19 com:

- Evolução temporal de casos e mortes
- Comparação entre países
- Impacto da vacinação na pandemia

**Fonte de dados:** Our World in Data (CSV público atualizado)

---

## 🏗️ ARQUITETURA DO PROJETO

### Estrutura de Diretórios (OBRIGATÓRIA)

```
backend/
├── config/          # Configurações (settings.py, .env)
├── controller/      # Entrada HTTP (rotas/endpoints)
├── db/              # Conexão com banco de dados
├── middleware/      # Interceptação de requisições
├── model/           # Estrutura de dados (entidades)
├── repositories/    # Acesso a dados (queries)
├── routes/          # Definição de rotas da API
├── services/        # Regras de negócio (lógica ETL)
├── tests/           # Testes unitários e integração
├── utils/           # Utilitários (download, helpers)
└── __init__.py

frontend/            # Interface (opcional)
cache/               # Cache de arquivos CSV
load_data.py         # Script executor do ETL
test_connection.py   # Teste de conexão PostgreSQL
requirements.txt     # Dependências Python
.ENV                 # Variáveis de ambiente
```

### Princípios Arquiteturais

**Separação de Responsabilidades:**
- `controller` → Entrada HTTP
- `service` → Regra de negócio
- `repository` → Acesso a dados
- `model` → Estrutura de dados
- `middleware` → Interceptação

**Boas Práticas Obrigatórias:**
- Clean Code
- SOLID
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- Código simples, legível e modular

---

## 🗄️ ESTRATÉGIA DE BANCO DE DADOS

### Arquitetura Híbrida (DuckDB + PostgreSQL)

```
CSV → DuckDB (processamento) → Pandas (redução) → PostgreSQL (persistência)
```

### Por que DuckDB?

**DuckDB** é um banco analítico embarcado (in-process) otimizado para análise de dados.

**Vantagens:**
1. **Performance em CSV**: Processa arquivos grandes (500MB+) diretamente
2. **Eficiência de Memória**: Filtra dados durante leitura (não carrega tudo na RAM)
3. **Velocidade**: 10-100x mais rápido que Pandas puro em agregações
4. **Zero Configuração**: Não precisa de servidor separado
5. **SQL Analítico**: Queries otimizadas para agregações complexas

**Exemplo de Eficiência:**
```python
# ❌ Pandas puro (lento, usa muita RAM)
df = pd.read_csv('huge.csv')  # Carrega tudo
df = df[df['country'].isin(countries)]  # Filtra depois

# ✅ DuckDB (rápido, eficiente)
duckdb.query("SELECT * FROM 'huge.csv' WHERE country IN (...)")  # Filtra durante leitura
```

### Por que PostgreSQL?

- **Persistência confiável**: Dados estruturados e indexados
- **Queries complexas**: JOINs, agregações, análises temporais
- **Integridade**: ACID, constraints, transações
- **Produção**: Escalável e robusto

---

## 🔄 PIPELINE ETL

### ETAPA 1 — EXTRAÇÃO

- Download automático do CSV da fonte oficial
- URL: `https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv`
- Cache local para evitar downloads repetidos
- Sempre dados atualizados

### ETAPA 2 — TRANSFORMAÇÃO (DuckDB)

**Processamento:**
1. Ler CSV via DuckDB (não Pandas direto)
2. Filtrar 37 países/regiões prioritários durante leitura
3. Selecionar período: 2020-01-01 a 2023-12-31

**Colunas Selecionadas:**
- `location` → renomear para `country`
- `date`
- `total_cases`
- `new_cases`
- `total_deaths`
- `new_deaths`
- `total_vaccinations`
- `people_vaccinated`

**Tratamento de Dados:**
- Substituir nulos por 0 (quando aplicável)
- Converter tipos corretamente
- Ordenar por país e data

### ETAPA 3 — CARGA (PostgreSQL)

- Inserir na tabela `covid_data`
- Evitar duplicação (estratégia: truncate ou upsert)
- Usar conexão via `.ENV`
- Garantir integridade dos dados

---

## 📦 INSTALAÇÃO

### Pré-requisitos

- Python 3.x
- PostgreSQL instalado e rodando
- pip (gerenciador de pacotes Python)

### Instalar Dependências

```bash
pip install -r requirements.txt
```

### Dependências Principais

```
psycopg2-binary  # Conexão PostgreSQL
duckdb           # Processamento analítico
pandas           # Manipulação de dados
requests         # Download de arquivos
python-dotenv    # Variáveis de ambiente
```

---

## ⚙️ CONFIGURAÇÃO

### Arquivo `.ENV`

Criar arquivo `.ENV` na raiz do projeto:

```env
db_name=covidanalise
db_user=postgres
db_password=postgres
db_host=localhost
db_port=5432
```

### Criar Banco de Dados

```sql
CREATE DATABASE covidanalise;
```

---

## 🚀 EXECUÇÃO

### Testar Conexão

```bash
python test_connection.py
```

### Executar Pipeline ETL

```bash
python load_data.py
```

**Saída Esperada:**
```
✅ ETL CONCLUÍDO COM SUCESSO!
📊 Total de registros: XXX,XXX
🌍 Países carregados: 37
📅 Período: 2020-01-01 a 2023-12-31
```

---

## 📊 DADOS CARREGADOS

- **Período:** 2020-01-01 a 2023-12-31 (início, pico, vacinação)
- **Países:** 37 entidades (30 países + 7 agregações continentais)

### 🌍 Países Incluídos

China, India, United States, Indonesia, Pakistan, Brazil, Nigeria, Bangladesh, Russia, Mexico, Japan, Philippines, Egypt, Vietnam, Germany, United Kingdom, France, Italy, Spain, Turkey, Argentina, Colombia, Iran, South Africa, Canada, Peru, Chile, Netherlands, Belgium, Sweden

**Agregações:** World, Europe, Asia, North America, South America, Africa, Oceania

---

## 🔌 API (PLANEJADA)

### Endpoints Esperados

- `GET /countries` - Lista países disponíveis
- `GET /evolution` - Evolução temporal de casos/mortes
- `GET /compare` - Comparação entre países
- `GET /vaccination` - Impacto da vacinação

---

## 🔧 STACK TÉCNICA

- **Python 3.x** - Linguagem principal
- **DuckDB** - Processamento analítico de CSV
- **Pandas** - Manipulação de dados
- **PostgreSQL** - Banco de dados relacional
- **Requests** - Download de dados
- **psycopg2** - Driver PostgreSQL
- **python-dotenv** - Gerenciamento de variáveis de ambiente

---

## 🤝 METODOLOGIA DE DESENVOLVIMENTO

### Pair Programming (Júnior Executor + Sênior Decisor)

Este projeto segue uma dinâmica de **pair programming** onde:

**IA (Assistente) = Desenvolvedor JÚNIOR Executor**
- Executa com precisão
- Questiona quando necessário
- Sugere melhorias COM justificativa técnica
- Segue rigorosamente boas práticas
- **NÃO toma decisões sozinho**
- **NÃO implementa sem validação**

**Você (Humano) = Engenheiro SÊNIOR Decisor**
- Toma TODAS as decisões finais
- Aprova planos de execução
- Valida implementações
- Define prioridades

### ⚠️ REGRA PRINCIPAL

Antes de escrever QUALQUER linha de código, o assistente DEVE:

1. ✅ Analisar todo o escopo
2. ✅ Levantar dúvidas técnicas
3. ✅ Sugerir melhorias (com justificativa)
4. ✅ Criar um plano de execução completo
5. ✅ Aguardar aprovação do engenheiro sênior

🚫 **PROIBIDO** começar a codar sem plano aprovado

### 🚫 RESTRIÇÕES

- NÃO usar frameworks desnecessários
- NÃO complicar arquitetura
- NÃO fugir do escopo definido
- NÃO decidir sozinho sobre mudanças estruturais

### 🔍 OBSERVABILIDADE

Sempre implementar:
- Logs informativos
- Tratamento de erros adequado
- Validação de dados

---

## 📝 CONTRIBUINDO

Se outra IA ou desenvolvedor abrir este projeto:

1. Leia este README completamente
2. Entenda a arquitetura e separação de responsabilidades
3. Respeite a metodologia de pair programming
4. Siga as boas práticas definidas
5. Sempre crie plano de execução antes de implementar
6. Aguarde aprovação antes de modificar código

---

## 📄 LICENÇA

Projeto educacional - Análise de dados públicos COVID-19

---

## 🔗 REFERÊNCIAS

- **Fonte de Dados:** [Our World in Data - COVID-19](https://github.com/owid/covid-19-data)
- **DuckDB:** [https://duckdb.org/](https://duckdb.org/)
- **PostgreSQL:** [https://www.postgresql.org/](https://www.postgresql.org/)
