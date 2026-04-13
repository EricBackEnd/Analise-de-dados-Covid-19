# 🏗️ ARQUITETURA DO PROJETO

## Estrutura de Diretórios (OBRIGATÓRIA)

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

frontend/            # Interface React
docs/                # Documentação do projeto
cache/               # Cache de arquivos CSV
load_data.py         # Script executor do ETL
validate_data.py     # Script de validação de dados
test_connection.py   # Teste de conexão PostgreSQL
app.py               # Aplicação FastAPI
requirements.txt     # Dependências Python
.ENV                 # Variáveis de ambiente
```

---

## Princípios Arquiteturais

### Separação de Responsabilidades

- **controller** → Entrada HTTP (recebe requisições, valida entrada)
- **service** → Regra de negócio (lógica ETL, processamento)
- **repository** → Acesso a dados (queries SQL, CRUD)
- **model** → Estrutura de dados (entidades, schemas)
- **middleware** → Interceptação (logs, autenticação, CORS)
- **routes** → Definição de rotas (mapeamento URL → controller)
- **utils** → Utilitários (download, helpers genéricos)
- **config** → Configurações (settings, variáveis de ambiente)

### Fluxo de Requisição

```
Cliente → routes → middleware → controller → service → repository → database
                                                ↓
                                              model
```

---

## Boas Práticas Obrigatórias

### Clean Code
- Nomes descritivos e significativos
- Funções pequenas e focadas (uma responsabilidade)
- Comentários apenas quando necessário (código auto-explicativo)
- Formatação consistente

### SOLID

**S - Single Responsibility Principle**
- Cada classe/função tem uma única responsabilidade
- Exemplo: `covid_repository.py` só acessa dados, não processa

**O - Open/Closed Principle**
- Aberto para extensão, fechado para modificação
- Usar herança e composição

**L - Liskov Substitution Principle**
- Subclasses devem ser substituíveis por suas classes base

**I - Interface Segregation Principle**
- Interfaces específicas são melhores que genéricas

**D - Dependency Inversion Principle**
- Depender de abstrações, não de implementações concretas

### DRY (Don't Repeat Yourself)
- Evitar duplicação de código
- Criar funções reutilizáveis
- Centralizar configurações

### KISS (Keep It Simple, Stupid)
- Código simples e direto
- Evitar over-engineering
- Não usar frameworks desnecessários

---

## Stack Técnica

### Backend
- **Python 3.x** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **DuckDB** - Processamento analítico de CSV
- **Pandas** - Manipulação de dados
- **PostgreSQL** - Banco de dados relacional
- **psycopg2** - Driver PostgreSQL
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **pytest** - Framework de testes

### Frontend
- **React** - Biblioteca JavaScript para UI
- **Plotly** - Biblioteca de gráficos interativos
- **Axios** - Cliente HTTP para consumir API

---

## Padrões de Código

### Nomenclatura

**Arquivos:**
- snake_case: `covid_repository.py`, `etl_service.py`

**Classes:**
- PascalCase: `DatabaseConfig`, `CovidModel`

**Funções/Variáveis:**
- snake_case: `get_connection()`, `total_cases`

**Constantes:**
- UPPER_SNAKE_CASE: `CSV_URL`, `DATE_START`

### Estrutura de Funções

```python
def function_name(param1, param2):
    """
    Descrição breve da função.
    
    Args:
        param1: Descrição do parâmetro
        param2: Descrição do parâmetro
        
    Returns:
        Descrição do retorno
        
    Raises:
        Exception: Quando ocorre erro
    """
    # Implementação
    pass
```

---

## Observabilidade

### Logs
- Usar módulo `logging` do Python
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Formato: `%(asctime)s - %(levelname)s - %(message)s`

### Tratamento de Erros
- Try-except em operações críticas
- Mensagens de erro descritivas
- Rollback em transações de banco

### Validação
- Validar entrada de dados
- Verificar tipos e formatos
- Retornar erros apropriados
