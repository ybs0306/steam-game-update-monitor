@echo off
REM cd directory to the current BAT file path
cd /d "%~dp0"

uv run main.py
