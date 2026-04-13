"""
Schema SQL para tabela covid_data.
Define estrutura da tabela e índices.
"""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS covid_data (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    total_cases FLOAT DEFAULT 0,
    new_cases FLOAT DEFAULT 0,
    total_deaths FLOAT DEFAULT 0,
    new_deaths FLOAT DEFAULT 0,
    total_vaccinations FLOAT DEFAULT 0,
    people_vaccinated FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country, date)
);
"""

CREATE_INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_country_date ON covid_data(country, date);
CREATE INDEX IF NOT EXISTS idx_date ON covid_data(date);
CREATE INDEX IF NOT EXISTS idx_country ON covid_data(country);
"""
