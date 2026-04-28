#!/usr/bin/env python
"""Create FastAPI database and test connection"""
import psycopg
import sys
import time

def create_database():
    """Create fastapi_db database"""
    try:
        print("\n1. Connecting to PostgreSQL (postgres database)...")
        conn = psycopg.connect(
            dbname='postgres',
            user='postgres',
            password='password',
            host='localhost',
            port=5432,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        print("✓ Connected!")
        
        print("\n2. Checking if 'fastapi_db' exists...")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'fastapi_db'")
        exists = cursor.fetchone()
        
        if exists:
            print("✓ Database 'fastapi_db' already exists")
        else:
            print("✓ Creating 'fastapi_db'...")
            # Connection must be in autocommit mode for CREATE DATABASE
            conn.autocommit = True
            cursor.execute("CREATE DATABASE fastapi_db")
            print("✓ Database 'fastapi_db' created successfully!")
        
        cursor.close()
        conn.close()
        
        print("\n3. Testing connection to fastapi_db...")
        time.sleep(1)
        
        conn = psycopg.connect(
            dbname='fastapi_db',
            user='postgres',
            password='password',
            host='localhost',
            port=5432,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✓ Test query result: {result}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ SUCCESS! PostgreSQL is ready!")
        print("="*60)
        print("\nConnection Details:")
        print("  Host: localhost")
        print("  Port: 5432")
        print("  User: postgres")
        print("  Password: password")
        print("  Database: fastapi_db")
        print("\nConnection String:")
        print("  postgresql+psycopg://postgres:password@localhost:5432/fastapi_db")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {type(e).__name__}")
        print(f"  {str(e)}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Password is set to 'password'")
        print("  3. Run the reset_postgres_admin.py script first if you haven't already")
        return False

if __name__ == "__main__":
    try:
        success = create_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n✗ Cancelled by user")
        sys.exit(1)
