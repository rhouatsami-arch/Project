@echo off
REM Read the file and replace scram-sha-256 with trust for localhost
setlocal enabledelayedexpansion
set input_file=C:\Program Files\PostgreSQL\18\data\pg_hba.conf
set temp_file=%TEMP%\pg_hba_temp.conf

(for /f "delims=" %%a in ('type "%input_file%"') do (
    set line=%%a
    if "!line:~0,5!"=="host " (
        set line=!line:scram-sha-256=trust!
    )
    echo !line!
)) > "%temp_file%"

REM Copy the modified file back
copy /Y "%temp_file%" "%input_file%"
del "%temp_file%"

echo pg_hba.conf updated. Restarting PostgreSQL...
net stop postgresql-x64-18
timeout /t 2
net start postgresql-x64-18
timeout /t 3

echo Resetting password...
"C:\Program Files\PostgreSQL\18\bin\psql" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD '1234';"

echo Reverting pg_hba.conf...
(for /f "delims=" %%a in ('type "%input_file%"') do (
    set line=%%a
    if "!line:~0,5!"=="host " (
        set line=!line:trust=scram-sha-256!
    )
    echo !line!
)) > "%temp_file%"

copy /Y "%temp_file%" "%input_file%"
del "%temp_file%"

net stop postgresql-x64-18
timeout /t 2
net start postgresql-x64-18
timeout /t 3

echo Done! PostgreSQL restarted with original authentication.
