@echo off
start cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn app.main:app --reload"
start cmd /k "cd /d %~dp0frontend && npm run dev"