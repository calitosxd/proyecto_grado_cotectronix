#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Carga y Gestión de Datos OLAP - Invernadero COTECNOVA (Fase 2)
Soporta:
1. Motor In-Memory de Ultra-Alta Velocidad vía Polars (cero configuración requerida).
2. Conexión opcional a MySQL (invernadero_olap_fase2).
"""

import sys
from pathlib import Path
from typing import Dict, Tuple, Optional

# Garantizar que el directorio raíz del proyecto esté en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import polars as pl
import pandas as pd
import streamlit as st

# Metadatos dimensionales de sensores
SENSORES_DATA = [
    {"id_sensor": 1, "codigo_variable": "DHT20_TEMP_INT", "nombre_sensor": "DHT20 Interior", "variable_medida": "Temperatura Ambiental", "ubicacion": "Interior", "unidad_medida": "°C", "rango_min_optimo": 18.0, "rango_max_optimo": 28.0, "limite_alerta_inferior": 10.0, "limite_alerta_superior": 38.0},
    {"id_sensor": 2, "codigo_variable": "DHT20_HUM_INT", "nombre_sensor": "DHT20 Interior", "variable_medida": "Humedad Relativa", "ubicacion": "Interior", "unidad_medida": "%", "rango_min_optimo": 60.0, "rango_max_optimo": 80.0, "limite_alerta_inferior": 40.0, "limite_alerta_superior": 95.0},
    {"id_sensor": 3, "codigo_variable": "DHT20_TEMP_EXT", "nombre_sensor": "DHT20 Exterior", "variable_medida": "Temperatura Ambiental", "ubicacion": "Exterior", "unidad_medida": "°C", "rango_min_optimo": 15.0, "rango_max_optimo": 32.0, "limite_alerta_inferior": 8.0, "limite_alerta_superior": 42.0},
    {"id_sensor": 4, "codigo_variable": "DHT20_HUM_EXT", "nombre_sensor": "DHT20 Exterior", "variable_medida": "Humedad Relativa", "ubicacion": "Exterior", "unidad_medida": "%", "rango_min_optimo": 50.0, "rango_max_optimo": 85.0, "limite_alerta_inferior": 30.0, "limite_alerta_superior": 100.0},
    {"id_sensor": 5, "codigo_variable": "BH1750_LUX_INT", "nombre_sensor": "BH1750 Interior", "variable_medida": "Luminosidad", "ubicacion": "Interior", "unidad_medida": "Lux", "rango_min_optimo": 10000.0, "rango_max_optimo": 35000.0, "limite_alerta_inferior": 1000.0, "limite_alerta_superior": 50000.0},
    {"id_sensor": 6, "codigo_variable": "BH1750_LUX_EXT", "nombre_sensor": "BH1750 Exterior", "variable_medida": "Luminosidad", "ubicacion": "Exterior", "unidad_medida": "Lux", "rango_min_optimo": 15000.0, "rango_max_optimo": 50000.0, "limite_alerta_inferior": 2000.0, "limite_alerta_superior": 65000.0},
    {"id_sensor": 7, "codigo_variable": "LM393_SUE_100", "nombre_sensor": "LM393 Surco 1", "variable_medida": "Humedad Suelo 100%", "ubicacion": "Surco 1", "unidad_medida": "%", "rango_min_optimo": 70.0, "rango_max_optimo": 95.0, "limite_alerta_inferior": 40.0, "limite_alerta_superior": 100.0},
    {"id_sensor": 8, "codigo_variable": "LM393_SUE_75", "nombre_sensor": "LM393 Surco 2", "variable_medida": "Humedad Suelo 75%", "ubicacion": "Surco 2", "unidad_medida": "%", "rango_min_optimo": 55.0, "rango_max_optimo": 80.0, "limite_alerta_inferior": 30.0, "limite_alerta_superior": 90.0},
    {"id_sensor": 9, "codigo_variable": "LM393_SUE_50", "nombre_sensor": "LM393 Surco 3", "variable_medida": "Humedad Suelo 50%", "ubicacion": "Surco 3", "unidad_medida": "%", "rango_min_optimo": 35.0, "rango_max_optimo": 60.0, "limite_alerta_inferior": 15.0, "limite_alerta_superior": 75.0},
]

# Metadatos dimensionales de surcos / tratamientos
SURCOS_DATA = [
    {"id_surco": 1, "nombre_surco": "Surco 100% Humedad", "humedad_objetivo_pct": 100, "num_bolsas_almacigo": 27, "cuadriculas": 3, "descripcion_tratamiento": "Tratamiento de alta saturación hídrica (3 cuadrículas de 9 bolsas)."},
    {"id_surco": 2, "nombre_surco": "Surco 75% Humedad", "humedad_objetivo_pct": 75, "num_bolsas_almacigo": 27, "cuadriculas": 3, "descripcion_tratamiento": "Tratamiento medio-alto óptimo (3 cuadrículas de 9 bolsas)."},
    {"id_surco": 3, "nombre_surco": "Surco 50% Humedad", "humedad_objetivo_pct": 50, "num_bolsas_almacigo": 27, "cuadriculas": 3, "descripcion_tratamiento": "Tratamiento de restricción hídrica (3 cuadrículas de 9 bolsas)."},
    {"id_surco": 4, "nombre_surco": "Ambiente General / N/A", "humedad_objetivo_pct": 0, "num_bolsas_almacigo": 0, "cuadriculas": 0, "descripcion_tratamiento": "No aplica para sensores ambientales de aire y luz."},
]

def obtener_ruta_csv() -> Path:
    base = Path(__file__).resolve().parents[1]
    csv_candidates = [
        base / "documentacion_fase1" / "backup_servidor" / "datos_sensores_2024-04-16_a_2026-04-16.-v2csv.csv",
        base / "documentacion_fase1" / "Proyecto_Original" / "Proyecto_Original" / "BD_DBeaver" / "datos_sensores_2024-11-01_a_2025-10-02.csv"
    ]
    for c in csv_candidates:
        if c.is_file():
            return c
    raise FileNotFoundError("No se encontró el dataset histórico CSV del invernadero.")

@st.cache_data(show_spinner=False)
def cargar_dimensiones() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna los DataFrames de dim_sensor y dim_surco_suelo."""
    df_dim_sensor = pd.DataFrame(SENSORES_DATA)
    df_dim_surco = pd.DataFrame(SURCOS_DATA)
    return df_dim_sensor, df_dim_surco

@st.cache_data(show_spinner=True)
def cargar_modelo_olap_in_memory() -> Dict[str, pd.DataFrame]:
    """
    Ejecuta el proceso ETL columnar ultrarrápido con Polars
    y retorna las tablas del esquema en estrella junto con el DataFrame consolidado.
    """
    from scripts.etl_polars import cargar_y_limpiar_polars, transformar_olap_polars
    
    csv_path = obtener_ruta_csv()
    df_raw, _ = cargar_y_limpiar_polars(csv_path)
    df_tiempo_pl, df_hechos_pl, _ = transformar_olap_polars(df_raw)
    
    # Convertir a Pandas para máxima compatibilidad con Streamlit y Plotly
    df_dim_tiempo = df_tiempo_pl.to_pandas()
    df_fact = df_hechos_pl.to_pandas()
    df_dim_sensor, df_dim_surco = cargar_dimensiones()
    
    # Asegurar tipos datetime
    df_dim_tiempo['fecha_dt'] = pd.to_datetime(df_dim_tiempo['fecha'])
    df_dim_tiempo['fecha_hora_dt'] = pd.to_datetime(df_dim_tiempo['fecha_hora'])
    df_fact['fecha_hora_dt'] = pd.to_datetime(df_fact['fecha_hora'])
    
    # Crear DataFrame Analítico Consolidado (Join del Esquema en Estrella)
    df_olap = df_fact.merge(df_dim_sensor, on='id_sensor', how='left')
    df_olap = df_olap.merge(df_dim_surco, on='id_surco', how='left')
    df_olap = df_olap.merge(
        df_dim_tiempo[['id_tiempo', 'fecha', 'fecha_dt', 'anio', 'mes', 'nombre_mes', 'dia', 'hora', 'franja_horaria', 'dia_semana', 'trimestre', 'semana_anio', 'es_fin_de_semana']],
        on='id_tiempo',
        how='left'
    )
    
    return {
        "dim_sensor": df_dim_sensor,
        "dim_surco_suelo": df_dim_surco,
        "dim_tiempo": df_dim_tiempo,
        "fact_mediciones_invernadero": df_fact,
        "cubo_consolidado": df_olap
    }

def probar_conexion_mysql(host: str, user: str, password: str, database: str, port: int = 3306) -> Tuple[bool, str]:
    """Verifica si la conexión a MySQL es exitosa."""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connection_timeout=3
        )
        conn.close()
        return True, "Conexión a MySQL exitosa."
    except Exception as e:
        return False, str(e)

@st.cache_data(show_spinner=True)
def cargar_modelo_olap_mysql(host: str, user: str, password: str, database: str, port: int = 3306) -> Dict[str, pd.DataFrame]:
    """Carga los datos directamente desde la base de datos MySQL."""
    import mysql.connector
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    
    df_dim_sensor = pd.read_sql("SELECT * FROM dim_sensor;", conn)
    df_dim_surco = pd.read_sql("SELECT * FROM dim_surco_suelo;", conn)
    df_dim_tiempo = pd.read_sql("SELECT * FROM dim_tiempo;", conn)
    df_fact = pd.read_sql("SELECT * FROM fact_mediciones_invernadero;", conn)
    conn.close()
    
    df_dim_tiempo['fecha_dt'] = pd.to_datetime(df_dim_tiempo['fecha'])
    df_dim_tiempo['fecha_hora_dt'] = pd.to_datetime(df_dim_tiempo['fecha_hora'])
    df_fact['fecha_hora_dt'] = pd.to_datetime(df_fact['fecha_hora'])
    
    df_olap = df_fact.merge(df_dim_sensor, on='id_sensor', how='left')
    df_olap = df_olap.merge(df_dim_surco, on='id_surco', how='left')
    df_olap = df_olap.merge(
        df_dim_tiempo[['id_tiempo', 'fecha', 'fecha_dt', 'anio', 'mes', 'nombre_mes', 'dia', 'hora', 'franja_horaria', 'dia_semana', 'trimestre', 'semana_anio', 'es_fin_de_semana']],
        on='id_tiempo',
        how='left'
    )
    
    return {
        "dim_sensor": df_dim_sensor,
        "dim_surco_suelo": df_dim_surco,
        "dim_tiempo": df_dim_tiempo,
        "fact_mediciones_invernadero": df_fact,
        "cubo_consolidado": df_olap
    }
