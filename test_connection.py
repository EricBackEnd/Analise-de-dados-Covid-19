import psycopg2

try:
    conn = psycopg2.connect(
        dbname='analisecovid',
        user='postgres',
        password='postgres',
        host='localhost',
        port='5432'
    )
    print("✅ Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
