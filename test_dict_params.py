#!/usr/bin/env python
import os
import sys
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    print("1. Creating engine with dict parameters...")
    
    from sqlalchemy import create_engine
    
    # Instead of using a URL, use the URL with query parameters
    engine = create_engine(
        "postgresql://",
        creator=lambda: __import__('psycopg2').connect(
            dbname='fastapi_db',
            user='postgres',
            password='1234',
            host='localhost',
            port=5432,
            client_encoding='latin1'  # Use latin1 to avoid UTF-8 issues
        ),
        echo=False,
        pool_pre_ping=True
    )
    
    print("✅ Engine created")
    
    print("2. Attempting connection...")
    from sqlalchemy import text
    
    with engine.connect() as conn:
        print("✅ Connected!")
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"✅ Query successful! Result: {row}")
    
    print("\n✅✅✅ PostgreSQL CONNECTION SUCCESSFUL! ✅✅✅")
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)[:300]}")
    import traceback
    traceback.print_exc()
