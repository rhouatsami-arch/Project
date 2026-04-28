import psycopg2
from psycopg2 import sql

passwords = ['password', 'postgres', 'PASSWORD', '', '1234', '123456']

for pwd in passwords:
    try:
        # Try raw connection without encoding issues
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=pwd,
            host="localhost",
            port=5432,
            options="-c client_encoding=latin1"
        )
        print(f"✅ SUCCESS! Password is: '{pwd}'")
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print(f"✅ Query successful! Result: {result}")
        cur.close()
        conn.close()
        break
    except Exception as e:
        # Don't print the error (might have encoding issues)
        print(f"❌ Failed with password: '{pwd}'")
