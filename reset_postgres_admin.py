#!/usr/bin/env python
"""
PostgreSQL Password Reset Script
Requires: Administrator privileges
"""
import os
import subprocess
import time
import sys
import shutil

def run_cmd(cmd, wait_time=0):
    """Run a command and return result"""
    try:
        result = os.system(cmd)
        if wait_time > 0:
            time.sleep(wait_time)
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return -1

def backup_file(filepath):
    """Backup a file"""
    backup_path = filepath + '.backup'
    try:
        shutil.copy2(filepath, backup_path)
        print(f"✓ Backed up: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ Backup failed: {e}")
        return None

def read_file(filepath):
    """Read file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"✗ Read failed: {e}")
        return None

def write_file(filepath, content):
    """Write file content"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Write failed: {e}")
        return False

def modify_pg_hba_to_trust(filepath):
    """Change authentication to trust"""
    content = read_file(filepath)
    if not content:
        return False
    
    lines = content.split('\n')
    modified = []
    changed = False
    
    for line in lines:
        if line.startswith('host') and 'all' in line and '127.0.0.1' in line:
            if 'scram-sha-256' in line:
                new_line = line.replace('scram-sha-256', 'trust')
                modified.append(new_line)
                print(f"  Changed: {line[:50]}... -> trust")
                changed = True
            elif 'md5' in line:
                new_line = line.replace('md5', 'trust')
                modified.append(new_line)
                print(f"  Changed: {line[:50]}... -> trust")
                changed = True
            else:
                modified.append(line)
        else:
            modified.append(line)
    
    if changed:
        return write_file(filepath, '\n'.join(modified))
    else:
        print("✗ No authentication method found to change")
        return False

def revert_pg_hba_to_original(filepath, backup_path):
    """Restore original pg_hba.conf"""
    try:
        shutil.copy2(backup_path, filepath)
        print(f"✓ Restored: {filepath}")
        return True
    except Exception as e:
        print(f"✗ Restore failed: {e}")
        return False

def reset_postgres_password(new_password='password'):
    """Reset postgres user password"""
    psql_path = r"C:\Program Files\PostgreSQL\18\bin\psql"
    cmd = f'"{psql_path}" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD \'{new_password}\';"'
    
    print(f"\n4. Resetting PostgreSQL password to '{new_password}'...")
    result = run_cmd(cmd, wait_time=1)
    if result == 0:
        print(f"✓ Password reset successfully!")
        return True
    else:
        print(f"✗ Password reset failed")
        return False

def test_connection(password='password'):
    """Test PostgreSQL connection"""
    print(f"\n5. Testing connection with new password...")
    try:
        import psycopg
        conn = psycopg.connect(
            dbname='postgres',
            user='postgres',
            password=password,
            host='localhost',
            port=5432,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"✓ Connection successful! Password works: '{password}'")
        return True
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)[:100]}")
        return False

def main():
    """Main function"""
    pg_hba_path = r"C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
    pg_service = "postgresql-x64-18"
    new_password = 'password'
    
    print("="*60)
    print("PostgreSQL Password Reset Script")
    print("="*60)
    
    # Check if file exists
    if not os.path.exists(pg_hba_path):
        print(f"✗ ERROR: pg_hba.conf not found at {pg_hba_path}")
        return False
    
    print(f"\n1. Backing up pg_hba.conf...")
    backup_path = backup_file(pg_hba_path)
    if not backup_path:
        return False
    
    print(f"\n2. Modifying pg_hba.conf to use 'trust' authentication...")
    if not modify_pg_hba_to_trust(pg_hba_path):
        print("✗ Failed to modify pg_hba.conf")
        return False
    
    print(f"\n3. Restarting PostgreSQL service...")
    print("   Stopping...")
    run_cmd(f"net stop {pg_service}", wait_time=2)
    
    print("   Starting...")
    run_cmd(f"net start {pg_service}", wait_time=3)
    
    # Reset password
    if not reset_postgres_password(new_password):
        print("✗ Failed to reset password, but continuing...")
    
    time.sleep(1)
    
    print(f"\n6. Reverting pg_hba.conf to original authentication method...")
    if not revert_pg_hba_to_original(pg_hba_path, backup_path):
        print("⚠ Warning: Could not revert pg_hba.conf")
    
    print(f"\n7. Restarting PostgreSQL with original settings...")
    print("   Stopping...")
    run_cmd(f"net stop {pg_service}", wait_time=2)
    
    print("   Starting...")
    run_cmd(f"net start {pg_service}", wait_time=3)
    
    print("\n" + "="*60)
    print("PostgreSQL Password Reset Complete!")
    print("="*60)
    print(f"\n✓ New password for 'postgres' user: {new_password}")
    print(f"✓ Use in connection string: postgresql://postgres:{new_password}@localhost:5432/your_db")
    print("\n" + "="*60)

if __name__ == "__main__":
    # Check for admin privileges
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        # Windows
        import ctypes
        try:
            is_admin = ctypes.windll.shell.IsUserAnAdmin()
        except:
            is_admin = False
    
    if not is_admin:
        print("⚠ WARNING: This script requires Administrator privileges!")
        print("Please run Command Prompt as Administrator and try again.")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)
