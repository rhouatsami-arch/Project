#!/usr/bin/env python
import os
import sys

# Set encoding variables BEFORE importing anything that uses psycopg2
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

# Now import
try:
    print("1. Setting environment variables for PostgreSQL...")
    
    print("2. Loading database module...")
    from app.database import engine
    print("✅ Database module loaded")
    
    from sqlalchemy import text, pool
    print("✅ SQLAlchemy loaded")
    
    print("3. Attempting raw connection using engine...")
    
    # Use engine directly
    dbapi_conn = engine.raw_connection()
    print("✅ Got dbapi connection")
    
    cursor = dbapi_conn.cursor()
    print("✅ Got cursor")
    
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    print(f"✅ Query successful! Result: {result}")
    
    cursor.close()
    dbapi_conn.close()
    
    print("\n✅✅✅ PostgreSQL CONNECTION SUCCESSFUL! ✅✅✅")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)[:200]}")
    import traceback
    traceback.print_exc()
