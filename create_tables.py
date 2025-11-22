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

# Create licenses table
cur.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        license_key VARCHAR(50) PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        stripe_customer_id VARCHAR(100),
        stripe_subscription_id VARCHAR(100)
    );
""")

# Create API logs table
cur.execute("""
    CREATE TABLE IF NOT EXISTS api_logs (
        id SERIAL PRIMARY KEY,
        license_key VARCHAR(50),
        endpoint VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

# Insert a test license
cur.execute("""
    INSERT INTO licenses (license_key, email, status, expires_at)
    VALUES ('TEST123', 'test@example.com', 'active', '2026-12-31 23:59:59')
    ON CONFLICT (license_key) DO NOTHING;
""")

conn.commit()
cur.close()
conn.close()

print("✅ Tables created successfully!")
print("✅ Test license 'TEST123' inserted!")
