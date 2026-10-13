@echo off
title Invernadero OLAP - COTECTRONIX
cd /d "%~dp0\.."
echo ====================================================================
echo  Iniciando Tablero Analitico OLAP - Invernadero COTECNOVA (Fase 2)
echo ====================================================================
echo.
streamlit run pag/app.py --server.headless=false
pause
