#!/usr/bin/env python
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("1. Loading database module...")
    from app.database import engine
    print("2. Database module loaded successfully")
    
    from sqlalchemy import text
    print("3. SQLAlchemy text imported")
    
    print("4. Attempting connection...")
    with engine.connect() as connection:
        print("5. Connection established!")
        result = connection.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"6. Query successful! Result: {row}")
        print("✅ PostgreSQL CONNECTION SUCCESSFUL!")
        
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
