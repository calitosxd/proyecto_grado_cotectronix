#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio rápido para el Tablero OLAP Streamlit - COTECTRONIX
Ejecución: python run_dashboard.py
"""
import sys
import subprocess
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent
    app_path = root_dir / "pag" / "app.py"
    
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    
    print("=" * 70)
    print("🌿 INICIANDO TABLERO ANALÍTICO OLAP - INVERNADERO COTECTRONIX")
    print("=" * 70)
    print(f"Ruta de la aplicación: {app_path}")
    print("Abriendo servidor en http://localhost:8501 ...")
    print("Presiona Ctrl + C para detener.")
    print("=" * 70)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

if __name__ == "__main__":
    main()
