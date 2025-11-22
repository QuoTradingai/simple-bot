import psycopg2

conn = psycopg2.connect(
    host="quotrading-db.postgres.database.azure.com",
    port=5432,
    dbname="quotrading",
    user="quotradingadmin",
    password="QuoTrade2024!SecureDB",
    sslmode="require"
)

cur = conn.cursor()
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'rl_experiences' 
    ORDER BY ordinal_position;
""")

print("Current table columns:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
