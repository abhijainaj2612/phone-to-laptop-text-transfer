@echo off
cd /d "%~dp0"
if exist .env for /f "usebackq tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
python -m pc_client.main
