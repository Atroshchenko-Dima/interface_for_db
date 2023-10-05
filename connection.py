import psycopg2
from parameters import params

def get_connection():
    with psycopg2.connect(**params) as conn:
        return conn


# Функция выполнения запроса
def execute_query(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
