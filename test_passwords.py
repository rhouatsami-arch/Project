import psycopg2

passwords = ['password', 'postgres', '', '12345', 'admin']

for pwd in passwords:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password=pwd,
            database="postgres"
        )
        print(f"✅ SUCCESS! Correct password is: '{pwd}'")
        conn.close()
        break
    except Exception as e:
        print(f"❌ Failed with password '{pwd}': {str(e)[:50]}")
