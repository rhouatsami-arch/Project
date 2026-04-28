import os
import subprocess
import time

pg_hba_path = r"C:\Program Files\PostgreSQL\18\data\pg_hba.conf"

# Read the file
with open(pg_hba_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace scram-sha-256 with trust for all lines starting with 'host'
lines = content.split('\n')
modified = []
for line in lines:
    if line.startswith('host') and 'scram-sha-256' in line:
        modified_line = line.replace('scram-sha-256', 'trust')
        print(f"Changed: {line} -> {modified_line}")
        modified.append(modified_line)
    else:
        modified.append(line)

new_content = '\n'.join(modified)

# Write back
with open(pg_hba_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✓ pg_hba.conf modified to use trust authentication")

# Restart PostgreSQL
print("Stopping PostgreSQL...")
os.system('net stop postgresql-x64-18')
time.sleep(2)

print("Starting PostgreSQL...")
os.system('net start postgresql-x64-18')
time.sleep(3)

# Reset password using psql
print("Resetting postgres password...")
os.system(r'"C:\Program Files\PostgreSQL\18\bin\psql" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD \'1234\';"')

print("✓ Password reset to: 1234")
time.sleep(1)

# Revert pg_hba.conf
print("Reverting pg_hba.conf to use scram-sha-256...")
lines = new_content.split('\n')
reverted = []
for line in lines:
    if line.startswith('host') and 'trust' in line:
        reverted_line = line.replace('trust', 'scram-sha-256')
        reverted.append(reverted_line)
    else:
        reverted.append(line)

reverted_content = '\n'.join(reverted)
with open(pg_hba_path, 'w', encoding='utf-8') as f:
    f.write(reverted_content)

print("✓ pg_hba.conf reverted")

# Restart PostgreSQL again
print("Restarting PostgreSQL with original authentication...")
os.system('net stop postgresql-x64-18')
time.sleep(2)
os.system('net start postgresql-x64-18')
time.sleep(3)

print("\n✅ All done! PostgreSQL is ready with password: 1234")
