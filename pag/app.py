#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
SISTEMA DE MONITOREO AMBIENTAL PARA INVERNADERO — FASE 2
SEMILLERO DE INVESTIGACIÓN COTECTRONIX — COTECNOVA
Tablero Analítico Multidimensional (OLAP) con Ralph Kimball Star Schema
====================================================================
"""

import sys
from pathlib import Path

# Garantizar resolución de módulos tanto si se ejecuta desde raíz como desde pag/
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PAG_DIR = Path(__file__).resolve().parent
if str(PAG_DIR) not in sys.path:
    sys.path.insert(0, str(PAG_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera llamada de Streamlit)
st.set_page_config(
    page_title="Invernadero OLAP · COTECTRONIX",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/calitosxd/fase1semillero',
        'About': "### Sistema de Monitoreo Ambiental e Inteligencia de Datos - Fase 2\nSemillero COTECTRONIX — Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)."
    }
)

# Importar estilos y cargador con soporte dual de rutas
try:
    from pag.styles import get_custom_css, render_kpi_card
    from pag.data_loader import (
        cargar_modelo_olap_in_memory,
        cargar_modelo_olap_mysql,
        probar_conexion_mysql
    )
    from pag.auth_ui import (
        render_login_view,
        render_sidebar_user_profile,
        render_admin_user_management,
        get_role_badge_html
    )
except ImportError:
    from styles import get_custom_css, render_kpi_card
    from data_loader import (
        cargar_modelo_olap_in_memory,
        cargar_modelo_olap_mysql,
        probar_conexion_mysql
    )
    from auth_ui import (
        render_login_view,
        render_sidebar_user_profile,
        render_admin_user_management,
        get_role_badge_html
    )

# Inyectar estilos CSS avanzados
st.markdown(get_custom_css(), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CONTROL DE ACCESO Y AUTENTICACIÓN (LOGIN & ROLES UML)
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Si el usuario NO está autenticado, renderizar la pantalla de Login y detener
if not st.session_state.logged_in:
    render_login_view()
    st.stop()

# Usuario autenticado en sesión actual
current_user = st.session_state.current_user or {}
user_role = current_user.get('rol', 'Investigador / Docente')
es_admin = "Administrador" in user_role

if 'data_source' not in st.session_state:
    st.session_state.data_source = 'memory'

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL (SIDEBAR) — CONTROLES Y FILTROS MULTIDIMENSIONALES
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 16px 0;">
        <span style="font-size: 2.8rem;">🌿</span>
        <h2 style="margin: 6px 0 0 0; font-size: 1.35rem; color: #f8fafc; font-weight: 800;">COTECTRONIX</h2>
        <p style="margin: 0; font-size: 0.8rem; color: #34d399; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Invernadero OLAP · Fase 2</p>
    </div>
    """, unsafe_allow_html=True)

    # Perfil del usuario autenticado en la barra lateral
    render_sidebar_user_profile()
    
    st.markdown("### ⚙️ Motor de Datos")
    fuente_seleccionada = st.radio(
        "Seleccionar origen:",
        ["⚡ In-Memory (Polars - Alta Velocidad)", "🐬 Base de Datos MySQL"],
        index=0 if st.session_state.data_source == 'memory' else 1,
        help="In-Memory ejecuta el proceso ETL directo con Polars en milisegundos. MySQL se conecta a la instancia local."
    )
    
    usar_mysql = "MySQL" in fuente_seleccionada
    datos_cargados = None
    
    if usar_mysql:
        st.markdown("#### 🔑 Credenciales MySQL")
        mysql_host = st.text_input("Host", value="localhost")
        mysql_port = st.number_input("Puerto", value=3306, step=1)
        mysql_user = st.text_input("Usuario", value="root")
        mysql_pass = st.text_input("Contraseña", type="password", value="")
        mysql_db = st.text_input("Base de datos", value="invernadero_olap_fase2")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔌 Conectar", use_container_width=True):
                ok, msg = probar_conexion_mysql(mysql_host, mysql_user, mysql_pass, mysql_db, int(mysql_port))
                if ok:
                    st.success(msg)
                    st.session_state.data_source = 'mysql'
                else:
                    st.error(f"Error: {msg}")
        with col_btn2:
            if st.button("Volver a Memory", use_container_width=True):
                st.session_state.data_source = 'memory'
                st.rerun()
                
        if st.session_state.data_source == 'mysql':
            try:
                datos_cargados = cargar_modelo_olap_mysql(mysql_host, mysql_user, mysql_pass, mysql_db, int(mysql_port))
            except Exception as e:
                st.warning(f"No se pudo cargar desde MySQL ({e}). Usando motor en memoria.")
                datos_cargados = cargar_modelo_olap_in_memory()
        else:
            datos_cargados = cargar_modelo_olap_in_memory()
    else:
        st.session_state.data_source = 'memory'
        datos_cargados = cargar_modelo_olap_in_memory()

    st.markdown("---")
    st.markdown("### 🔍 Filtros Multidimensionales (Slice & Dice)")
    
    df_cubo_total = datos_cargados["cubo_consolidado"]
    
    # Filtro Temporal: Rango de Fechas
    fecha_min = df_cubo_total['fecha_dt'].min().date()
    fecha_max = df_cubo_total['fecha_dt'].max().date()
    
    rango_fechas = st.date_input(
        "📅 Período de Tiempo",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        help="Filtra mediciones según la fecha de captura."
    )
    
    if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2:
        f_inicio, f_fin = rango_fechas
    elif isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 1:
        f_inicio = f_fin = rango_fechas[0]
    else:
        f_inicio, f_fin = fecha_min, fecha_max
        
    franjas_disponibles = sorted(df_cubo_total['franja_horaria'].dropna().unique().tolist())
    franjas_sel = st.multiselect(
        "⏰ Franja Horaria",
        options=franjas_disponibles,
        default=franjas_disponibles,
        help="Madrugada (00-05), Mañana (06-11), Tarde (12-17), Noche (18-23)"
    )
    
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    dias_disponibles = [d for d in dias_orden if d in df_cubo_total['dia_semana'].unique()]
    dias_sel = st.multiselect(
        "📆 Días de la Semana",
        options=dias_disponibles,
        default=dias_disponibles
    )
    
    magnitudes_disp = sorted(df_cubo_total['variable_medida'].dropna().unique().tolist())
    magnitudes_sel = st.multiselect(
        "📡 Magnitud Física",
        options=magnitudes_disp,
        default=magnitudes_disp
    )
    
    surcos_disp = sorted(df_cubo_total['nombre_surco'].dropna().unique().tolist())
    surcos_sel = st.multiselect(
        "🌱 Tratamiento / Surco",
        options=surcos_disp,
        default=surcos_disp
    )
    
    st.markdown("---")
    
    mask = (
        (df_cubo_total['fecha_dt'].dt.date >= f_inicio) &
        (df_cubo_total['fecha_dt'].dt.date <= f_fin) &
        (df_cubo_total['franja_horaria'].isin(franjas_sel)) &
        (df_cubo_total['dia_semana'].isin(dias_sel)) &
        (df_cubo_total['variable_medida'].isin(magnitudes_sel)) &
        (df_cubo_total['nombre_surco'].isin(surcos_sel))
    )
    
    df_filtrado = df_cubo_total[mask].copy()
    
    total_total = len(df_cubo_total)
    total_filtrado = len(df_filtrado)
    pct_filtrado = (total_filtrado / total_total * 100) if total_total > 0 else 0
    
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 12px; padding: 14px; margin-top: 10px;">
        <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Registros en Selección</div>
        <div style="font-size: 1.6rem; font-weight: 850; color: #38bdf8; margin: 4px 0;">{total_filtrado:,} <span style="font-size: 0.9rem; font-weight: 500; color: #94a3b8;">/ {total_total:,}</span></div>
        <div style="font-size: 0.85rem; color: #34d399; font-weight: 600;">{pct_filtrado:.1f}% del cubo analítico</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Restablecer Filtros", use_container_width=True):
        st.rerun()

# -----------------------------------------------------------------------------
# 4. ENCABEZADO PRINCIPAL (HERO SECTION)
# -----------------------------------------------------------------------------
user_badge = f'<span class="hero-badge" style="background: rgba(245, 158, 11, 0.18); border-color: rgba(245, 158, 11, 0.4); color: #fbbf24;">🟡 {current_user.get("nombre_completo", "Admin")} ({user_role})</span>' if es_admin else f'<span class="hero-badge" style="background: rgba(16, 185, 129, 0.18); border-color: rgba(52, 211, 153, 0.4); color: #34d399;">🟢 {current_user.get("nombre_completo", "Investigador")} ({user_role})</span>'

st.markdown(f"""
<div class="hero-header">
    <div>
        <div style="display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
            <span class="hero-badge">🏛️ Ralph Kimball Star Schema</span>
            <span class="hero-badge" style="background: rgba(6, 182, 212, 0.18); border-color: rgba(6, 182, 212, 0.4); color: #38bdf8;">⚡ Polars Rust Engine</span>
            <span class="hero-badge" style="background: rgba(168, 85, 247, 0.18); border-color: rgba(168, 85, 247, 0.4); color: #c084fc;">🎓 COTECNOVA 2026</span>
            {user_badge}
        </div>
        <h1 class="hero-title">Sistema de Monitoreo Ambiental e Inteligencia OLAP</h1>
        <p class="hero-subtitle">Visualización analítica multidimensional de microclima e indicadores agronómicos para invernadero automatizado.</p>
    </div>
    <div>
        <div class="info-pill">
            <span style="color: #34d399; font-size: 1.1rem;">●</span> Origen: <strong>{'MySQL Server' if usar_mysql else 'In-Memory (Polars)'}</strong>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Plantilla oscura unificada y espaciosa para Plotly
PLOTLY_THEME = dict(
    layout=go.Layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        plot_bgcolor="rgba(15, 23, 42, 0.0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0", size=13),
        margin=dict(l=60, r=40, t=60, b=60),
        xaxis=dict(gridcolor="rgba(51, 65, 85, 0.35)", zerolinecolor="rgba(51, 65, 85, 0.6)", title_font=dict(size=14, color="#94a3b8")),
        yaxis=dict(gridcolor="rgba(51, 65, 85, 0.35)", zerolinecolor="rgba(51, 65, 85, 0.6)", title_font=dict(size=14, color="#94a3b8")),
        legend=dict(font=dict(size=13), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
)

# -----------------------------------------------------------------------------
# 5. PESTAÑAS ANALÍTICAS PRINCIPALES
# -----------------------------------------------------------------------------
tab_titles = [
    "📊 Resumen Ejecutivo",
    "🧊 Cubo Multidimensional (OLAP)",
    "⚠️ Detección de Anomalías",
    "🌱 Agronomía y Riego",
    "🌡️ Microclima: Interior vs Exterior",
    "🏛️ Esquema en Estrella (Kimball)"
]

if es_admin:
    tab_titles.append("👥 Gestión de Usuarios")

all_tabs = st.tabs(tab_titles)
tab1, tab2, tab3, tab4, tab5, tab6 = all_tabs[0], all_tabs[1], all_tabs[2], all_tabs[3], all_tabs[4], all_tabs[5]

# =============================================================================
# TAB 1: RESUMEN EJECUTIVO & KPIS CON ESPACIO GENEROSO
# =============================================================================
with tab1:
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;'>📌 Indicadores Clave de Desempeño (KPIs)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>Métricas fundamentales calculadas dinámicamente sobre la selección actual del cubo dimensional.</p>", unsafe_allow_html=True)
    
    num_capturas = df_filtrado['id_sensado_origen'].nunique() if total_filtrado > 0 else 0
    total_mediciones = len(df_filtrado)
    total_anomalias = int(df_filtrado['flag_anomalia'].sum()) if total_filtrado > 0 else 0
    tasa_anomalias = (total_anomalias / total_mediciones * 100) if total_mediciones > 0 else 0.0
    
    mediciones_suelo = df_filtrado[df_filtrado['variable_medida'].str.contains('Humedad Suelo', na=False)]
    horas_riego_req = int(mediciones_suelo['flag_riego'].sum()) if len(mediciones_suelo) > 0 else 0
    tasa_riego = (horas_riego_req / len(mediciones_suelo) * 100) if len(mediciones_suelo) > 0 else 0.0
    
    # Organización amplia: 2 filas de 2 columnas con tarjetas generosas
    kpi_col1, kpi_col2 = st.columns(2)
    with kpi_col1:
        st.markdown(render_kpi_card("⏱️", "Capturas Horarias Registradas", f"{num_capturas:,}", f"Período evaluado: {fecha_min} al {fecha_max}", "emerald", "positive"), unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(render_kpi_card("📊", "Mediciones Atómicas de Sensores", f"{total_mediciones:,}", "9 sensores desagregados en tabla de hechos", "cyan", "positive"), unsafe_allow_html=True)
        
    kpi_col3, kpi_col4 = st.columns(2)
    with kpi_col3:
        st.markdown(render_kpi_card("⚠️", "Anomalías Ambientales Detectadas", f"{total_anomalias:,}", f"{tasa_anomalias:.2f}% lecturas fuera de rango óptimo", "amber", "alert" if tasa_anomalias > 10 else "warning"), unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(render_kpi_card("💧", "Horas Acumuladas con Déficit Hídrico", f"{horas_riego_req:,} hrs", f"{tasa_riego:.1f}% del tiempo bajo humedad objetivo", "purple", "warning"), unsafe_allow_html=True)
        
    st.markdown("<div class='spacer-xl'></div>", unsafe_allow_html=True)
    
    # GRÁFICOS UNO BAJO EL OTRO CON GRAN ESPACIO Y ALTURA
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">📈 1. Evolución Temporal del Volumen de Mediciones y Anomalías por Mes</div>
        <div class="chart-desc">Comportamiento longitudinal que compara la densidad de sensado frente a la ocurrencia de eventos fuera de los rangos de seguridad ambiental.</div>
    """, unsafe_allow_html=True)
    
    if total_filtrado > 0:
        df_mes_agg = df_filtrado.groupby(['anio', 'mes', 'nombre_mes']).agg(
            total_lecturas=('valor_medido', 'count'),
            anomalias=('flag_anomalia', 'sum'),
            riego_req=('flag_riego', 'sum')
        ).reset_index()
        df_mes_agg['periodo'] = df_mes_agg['nombre_mes'] + ' ' + df_mes_agg['anio'].astype(str)
        df_mes_agg = df_mes_agg.sort_values(by=['anio', 'mes'])
        
        fig_mes = go.Figure()
        fig_mes.add_trace(go.Bar(
            x=df_mes_agg['periodo'],
            y=df_mes_agg['total_lecturas'],
            name="Lecturas Totales Registradas",
            marker_color="rgba(56, 189, 248, 0.45)",
            marker_line_color="#38bdf8",
            marker_line_width=1.5
        ))
        fig_mes.add_trace(go.Scatter(
            x=df_mes_agg['periodo'],
            y=df_mes_agg['anomalias'],
            name="Anomalías Ambientales (flag_anomalia = 1)",
            mode="lines+markers",
            line=dict(color="#f43f5e", width=3.5),
            marker=dict(size=9, symbol="diamond")
        ))
        fig_mes.update_layout(
            PLOTLY_THEME['layout'],
            height=520,
            xaxis_title="Período Mensual",
            yaxis_title="Cantidad de Registros",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("No hay datos disponibles para la combinación actual de filtros.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
    
    # SEGUNDO GRÁFICO: DISTRIBUCIÓN
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">🔬 2. Distribución y Peso Relativo de Mediciones por Magnitud Física</div>
        <div class="chart-desc">Proporción de mediciones registradas por cada tipología de sensor físico del invernadero.</div>
    """, unsafe_allow_html=True)
    
    if total_filtrado > 0:
        df_var_count = df_filtrado.groupby('variable_medida').size().reset_index(name='conteo')
        fig_donut = px.pie(
            df_var_count,
            names='variable_medida',
            values='conteo',
            hole=0.55,
            color_discrete_sequence=['#10b981', '#06b6d4', '#f59e0b', '#8b5cf6', '#ec4899']
        )
        fig_donut.update_layout(
            PLOTLY_THEME['layout'],
            height=480,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.05, font=dict(size=13))
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='spacer-xl'></div>", unsafe_allow_html=True)
    
    # ESTADO DETALLADO DE LOS SENSORES CON ESPACIO AMPLIO
    st.markdown("<h3 style='font-size: 1.4rem; font-weight: 800; color: #f8fafc; margin-bottom: 6px;'>📡 3. Catálogo de Sensores Físicos y Comportamiento Estadístico</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 0.92rem; margin-bottom: 24px;'>Detalle individual de cada uno de los 9 sensores del diseño IoT de Fase 1.</p>", unsafe_allow_html=True)
    
    df_sensor_summary = df_filtrado.groupby(['id_sensor', 'nombre_sensor', 'variable_medida', 'unidad_medida', 'ubicacion', 'rango_min_optimo', 'rango_max_optimo', 'limite_alerta_inferior', 'limite_alerta_superior']).agg(
        promedio=('valor_medido', 'mean'),
        minimo=('valor_medido', 'min'),
        maximo=('valor_medido', 'max'),
        desv=('valor_medido', 'std'),
        anomalias=('flag_anomalia', 'sum'),
        total=('valor_medido', 'count')
    ).reset_index()
    
    if len(df_sensor_summary) > 0:
        cols_sensor_cards = st.columns(2)
        for idx, row in df_sensor_summary.iterrows():
            with cols_sensor_cards[idx % 2]:
                tasa_s = (row['anomalias'] / row['total'] * 100) if row['total'] > 0 else 0
                badge_color = "#34d399" if tasa_s < 5 else ("#fbbf24" if tasa_s < 15 else "#f87171")
                desv_val = row['desv'] if not pd.isna(row['desv']) else 0.0
                st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(51, 65, 85, 0.6); border-radius: 16px; padding: 22px 26px; margin-bottom: 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.2);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 800; color: #f1f5f9; font-size: 1.15rem;">{row['nombre_sensor']}</span>
                        <span style="background: rgba(15, 23, 42, 0.85); border: 1px solid {badge_color}; color: {badge_color}; font-size: 0.8rem; padding: 4px 12px; border-radius: 16px; font-weight: 700;">{tasa_s:.1f}% anómalo</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px;">{row['variable_medida']} — Ubicación: <strong style="color: #cbd5e1;">{row['ubicacion']}</strong></div>
                    <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: baseline;">
                        <div>
                            <span style="font-size: 2.1rem; font-weight: 850; color: #38bdf8;">{row['promedio']:.2f}</span>
                            <span style="font-size: 1.0rem; color: #cbd5e1; font-weight: 600;"> {row['unidad_medida']}</span>
                            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">Desv. Estándar: ±{desv_val:.2f} {row['unidad_medida']}</div>
                        </div>
                        <div style="font-size: 0.84rem; color: #94a3b8; text-align: right; line-height: 1.6;">
                            <div>Min: <strong style="color:#f8fafc;">{row['minimo']:.1f}</strong> | Max: <strong style="color:#f8fafc;">{row['maximo']:.1f}</strong></div>
                            <div>Rango Óptimo: <strong style="color: #34d399;">[{row['rango_min_optimo']:.0f} - {row['rango_max_optimo']:.0f}]</strong></div>
                            <div>Alerta: <span style="color: #f87171;">&lt; {row['limite_alerta_inferior']:.0f} o &gt; {row['limite_alerta_superior']:.0f}</span></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: CUBO MULTIDIMENSIONAL (OPERACIONES OLAP)
# =============================================================================
with tab2:
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;'>🧊 Explorador del Cubo Multidimensional (OLAP)</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>
    Ejecución interactiva de operaciones multidimensionales: <strong>Slice & Dice</strong> (corte y subcubo), 
    <strong>Roll-Up & Drill-Down</strong> (navegación por jerarquías) y <strong>Pivot</strong> (rotación y agregación cruzada de dimensiones).
    </p>
    """, unsafe_allow_html=True)
    
    subtab_pivot, subtab_hier = st.tabs(["🔄 1. Tabla Dinámica OLAP (Pivot)", "🔽 2. Jerarquías Temporales (Roll-up / Drill-down)"])
    
    with subtab_pivot:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Configuración de Dimensiones y Agregación (Cubo OLAP)</div>
            <div class="chart-desc">Selecciona las dimensiones que se posicionarán en los ejes de filas y columnas, la métrica base y la función de agregación matemática.</div>
        """, unsafe_allow_html=True)
        
        opciones_dim = [
            ("nombre_sensor", "Sensor Físico"),
            ("variable_medida", "Magnitud Física"),
            ("ubicacion", "Ubicación (Interior / Exterior / Surco)"),
            ("nombre_surco", "Tratamiento / Surco de Suelo"),
            ("franja_horaria", "Franja Horaria del Día"),
            ("dia_semana", "Día de la Semana"),
            ("nombre_mes", "Mes del Año"),
            ("anio", "Año"),
            ("trimestre", "Trimestre"),
            ("es_fin_de_semana", "Fin de Semana (0 / 1)")
        ]
        
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            idx_filas = [x[0] for x in opciones_dim].index("nombre_sensor")
            dim_fila = st.selectbox(
                "Dimensión en Filas (Eje Y):",
                options=[x[0] for x in opciones_dim],
                format_func=lambda x: dict(opciones_dim)[x],
                index=idx_filas
            )
            
            metrica = st.selectbox(
                "Métrica a Evaluar:",
                ["valor_medido", "flag_anomalia", "flag_riego"],
                format_func=lambda x: {
                    "valor_medido": "Valor Medido por Sensor",
                    "flag_anomalia": "Bandera de Anomalía (0/1)",
                    "flag_riego": "Bandera de Déficit de Riego (0/1)"
                }[x]
            )
            
        with c_sel2:
            idx_cols = [x[0] for x in opciones_dim].index("franja_horaria")
            dim_col = st.selectbox(
                "Dimensión en Columnas (Eje X):",
                options=[x[0] for x in opciones_dim],
                format_func=lambda x: dict(opciones_dim)[x],
                index=idx_cols
            )
            
            agregacion = st.selectbox(
                "Función de Agregación:",
                ["mean", "sum", "count", "min", "max", "std"],
                format_func=lambda x: {
                    "mean": "Promedio (AVG)",
                    "sum": "Suma Total (SUM)",
                    "count": "Conteo de Mediciones (COUNT)",
                    "min": "Mínimo (MIN)",
                    "max": "Máximo (MAX)",
                    "std": "Desviación Estándar (STD)"
                }[x]
            )
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        if total_filtrado > 0:
            try:
                tabla_pivot = pd.pivot_table(
                    df_filtrado,
                    values=metrica,
                    index=dim_fila,
                    columns=dim_col,
                    aggfunc=agregacion,
                    fill_value=0
                )
                
                # GRÁFICO HEATMAP CON ALTURA Y ESPACIO GENEROSO
                st.markdown(f"""
                <div class="chart-card">
                    <div class="chart-title">🔥 Mapa de Calor del Cubo OLAP: {dict(opciones_dim)[dim_fila]} vs {dict(opciones_dim)[dim_col]}</div>
                    <div class="chart-desc">Intensidad cromática según el resultado de la función <strong>{agregacion.upper()}</strong> aplicada a <strong>{metrica}</strong>.</div>
                """, unsafe_allow_html=True)
                
                fig_heat_pivot = px.imshow(
                    tabla_pivot,
                    text_auto=".2f" if agregacion in ['mean', 'std'] else True,
                    aspect="auto",
                    color_continuous_scale="Viridis"
                )
                fig_heat_pivot.update_layout(
                    PLOTLY_THEME['layout'],
                    height=600,
                    xaxis_title=dict(opciones_dim)[dim_col],
                    yaxis_title=dict(opciones_dim)[dim_fila]
                )
                st.plotly_chart(fig_heat_pivot, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
                
                # TABLA DE DATOS PIVOT CON ESPACIO COMPLETO
                st.markdown("""
                <div class="chart-card">
                    <div class="chart-title">📋 Matriz Numérica Cruzada</div>
                    <div class="chart-desc">Celdas formateadas con valores consolidados. Verde indica máximos por columna y azul mínimos.</div>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    tabla_pivot.style.highlight_max(axis=0, color="#065f46").highlight_min(axis=0, color="#1e3a8a"),
                    use_container_width=True,
                    height=380
                )
                
                csv_pivot = tabla_pivot.to_csv().encode('utf-8')
                st.download_button(
                    "📥 Descargar Matriz Pivot en CSV",
                    csv_pivot,
                    f"pivot_{dim_fila}_{dim_col}_{metrica}.csv",
                    "text/csv"
                )
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al generar la tabla dinámica: {e}")
        else:
            st.warning("No hay suficientes registros para pivotear.")
            
    with subtab_hier:
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">Navegación Jerárquica Temporal (Roll-Up / Drill-Down)</div>
            <div class="chart-desc">Permite subir o bajar en la granularidad del tiempo para descubrir patrones estacionales, diurnos o macro-anuales.</div>
        """, unsafe_allow_html=True)
        
        nivel_jerarquia = st.select_slider(
            "Seleccionar Nivel Jerárquico de la Dimensión Tiempo:",
            options=["anio", "trimestre", "nombre_mes", "dia_semana", "franja_horaria", "hora"],
            value="nombre_mes",
            format_func=lambda x: {
                "anio": "1. Año (Nivel más consolidado - Roll-Up)",
                "trimestre": "2. Trimestre",
                "nombre_mes": "3. Mes",
                "dia_semana": "4. Día de la Semana",
                "franja_horaria": "5. Franja Horaria",
                "hora": "6. Hora del Día (Nivel más detallado - Drill-Down)"
            }[x]
        )
        
        if total_filtrado > 0:
            df_hier = df_filtrado.groupby([nivel_jerarquia, 'variable_medida']).agg(
                promedio=('valor_medido', 'mean'),
                anomalias=('flag_anomalia', 'sum'),
                lecturas=('valor_medido', 'count')
            ).reset_index()
            
            fig_hier = px.bar(
                df_hier,
                x=nivel_jerarquia,
                y='promedio',
                color='variable_medida',
                barmode='group',
                color_discrete_sequence=['#10b981', '#06b6d4', '#f59e0b', '#8b5cf6']
            )
            fig_hier.update_layout(
                PLOTLY_THEME['layout'],
                height=560,
                xaxis_title=nivel_jerarquia.capitalize(),
                yaxis_title="Promedio del Valor Medido"
            )
            st.plotly_chart(fig_hier, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 3: DETECCIÓN DE ANOMALÍAS (RF-07 / CU-09) — UNO BAJO EL OTRO
# =============================================================================
with tab3:
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;'>⚠️ Detección y Análisis de Anomalías Ambientales (RF-07)</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>
    Identificación automática de capturas fuera de los umbrales agronómicos críticos de seguridad definidos en la dimensión <code>dim_sensor</code>.
    </p>
    """, unsafe_allow_html=True)
    
    # 1. RANKING POR SENSOR A ANCHO COMPLETO
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">📊 1. Ranking de Ocurrencia de Anomalías por Sensor Físico</div>
        <div class="chart-desc">Cantidad absoluta y porcentaje de mediciones que traspasaron los límites de alerta superior o inferior.</div>
    """, unsafe_allow_html=True)
    
    if total_filtrado > 0:
        df_anom_sensor = df_filtrado.groupby(['nombre_sensor', 'variable_medida']).agg(
            total_anom=('flag_anomalia', 'sum'),
            total_obs=('valor_medido', 'count')
        ).reset_index()
        df_anom_sensor['tasa_pct'] = (df_anom_sensor['total_anom'] / df_anom_sensor['total_obs'] * 100).round(2)
        df_anom_sensor = df_anom_sensor.sort_values(by='total_anom', ascending=True)
        
        fig_bar_anom = px.bar(
            df_anom_sensor,
            x='total_anom',
            y='nombre_sensor',
            orientation='h',
            color='tasa_pct',
            color_continuous_scale='Reds',
            text='tasa_pct'
        )
        fig_bar_anom.update_traces(texttemplate='%{text:.1f}% anómalo', textposition='outside', textfont=dict(size=12, color="#f8fafc"))
        fig_bar_anom.update_layout(
            PLOTLY_THEME['layout'],
            height=540,
            xaxis_title="Número Absoluto de Anomalías Detectadas",
            yaxis_title="",
            coloraxis_colorbar=dict(title="% Anómalo", len=0.7)
        )
        st.plotly_chart(fig_bar_anom, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
    
    # 2. CONCENTRACIÓN POR FRANJA HORARIA A ANCHO COMPLETO
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">🕒 2. Concentración de Anomalías por Franja Horaria del Día</div>
        <div class="chart-desc">Permite diagnosticar si los excesos o caídas extremas se presentan de Madrugada, Mañana, Tarde o Noche.</div>
    """, unsafe_allow_html=True)
    
    if total_filtrado > 0:
        df_anom_franja = df_filtrado.groupby(['franja_horaria', 'variable_medida'])['flag_anomalia'].sum().reset_index()
        fig_anom_franja = px.bar(
            df_anom_franja,
            x='franja_horaria',
            y='flag_anomalia',
            color='variable_medida',
            barmode='group',
            color_discrete_sequence=['#f87171', '#fb923c', '#facc15', '#a78bfa']
        )
        fig_anom_franja.update_layout(
            PLOTLY_THEME['layout'],
            height=500,
            xaxis_title="Franja Horaria",
            yaxis_title="Cantidad de Anomalías"
        )
        st.plotly_chart(fig_anom_franja, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
    
    # 3. INSPECCIÓN DETALLADA CON BANDAS DE ALERTA A ANCHO COMPLETO
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">🎯 3. Inspección Longitudinal y Umbrales Críticos por Sensor</div>
        <div class="chart-desc">Serie temporal interactiva con demarcación exacta de los límites de alerta superior e inferior y el rango óptimo.</div>
    """, unsafe_allow_html=True)
    
    sensores_lista = df_filtrado['nombre_sensor'].unique().tolist()
    if len(sensores_lista) > 0:
        sensor_seleccionado = st.selectbox("Seleccionar Sensor para evaluar:", sensores_lista)
        df_sensor_sel = df_filtrado[df_filtrado['nombre_sensor'] == sensor_seleccionado].sort_values(by='fecha_hora_dt')
        
        if len(df_sensor_sel) > 0:
            r_min = df_sensor_sel['rango_min_optimo'].iloc[0]
            r_max = df_sensor_sel['rango_max_optimo'].iloc[0]
            lim_inf = df_sensor_sel['limite_alerta_inferior'].iloc[0]
            lim_sup = df_sensor_sel['limite_alerta_superior'].iloc[0]
            unidad = df_sensor_sel['unidad_medida'].iloc[0]
            
            fig_scatter_anom = go.Figure()
            
            df_normal = df_sensor_sel[df_sensor_sel['flag_anomalia'] == 0]
            df_anom = df_sensor_sel[df_sensor_sel['flag_anomalia'] == 1]
            
            fig_scatter_anom.add_trace(go.Scatter(
                x=df_normal['fecha_hora_dt'],
                y=df_normal['valor_medido'],
                mode='lines',
                name='Lectura Normal (Dentro de límites)',
                line=dict(color='#06b6d4', width=1.2)
            ))
            
            if len(df_anom) > 0:
                fig_scatter_anom.add_trace(go.Scatter(
                    x=df_anom['fecha_hora_dt'],
                    y=df_anom['valor_medido'],
                    mode='markers',
                    name='Anomalía Crítica (flag_anomalia = 1)',
                    marker=dict(color='#ef4444', size=7, symbol='x')
                ))
                
            fig_scatter_anom.add_hline(y=lim_sup, line_dash="dash", line_color="#ef4444", line_width=2, annotation_text=f"Alerta Superior ({lim_sup} {unidad})", annotation_position="top left", annotation_font=dict(color="#f87171"))
            fig_scatter_anom.add_hline(y=lim_inf, line_dash="dash", line_color="#ef4444", line_width=2, annotation_text=f"Alerta Inferior ({lim_inf} {unidad})", annotation_position="bottom left", annotation_font=dict(color="#f87171"))
            fig_scatter_anom.add_hline(y=r_max, line_dash="dot", line_color="#10b981", annotation_text=f"Óptimo Máx ({r_max} {unidad})", annotation_font=dict(color="#34d399"))
            fig_scatter_anom.add_hline(y=r_min, line_dash="dot", line_color="#10b981", annotation_text=f"Óptimo Mín ({r_min} {unidad})", annotation_font=dict(color="#34d399"))
            
            fig_scatter_anom.update_layout(
                PLOTLY_THEME['layout'],
                height=560,
                xaxis_title="Línea de Tiempo (Fecha y Hora)",
                yaxis_title=f"Valor Registrado ({unidad})"
            )
            st.plotly_chart(fig_scatter_anom, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 4: AGRONOMÍA Y RIEGO (RF-08 / CU-10 / CU-11) — UNO BAJO EL OTRO
# =============================================================================
with tab4:
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;'>🌱 Balance Hídrico y Comparativa de Tratamientos (RF-08)</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>
    Evaluación comparativa de los tres tratamientos agronómicos de suelo del diseño experimental:
    <strong>Surco 1</strong> (100% de humedad objetivo), <strong>Surco 2</strong> (75% de humedad objetivo) y 
    <strong>Surco 3</strong> (50% de humedad objetivo).
    </p>
    """, unsafe_allow_html=True)
    
    df_suelo = df_filtrado[df_filtrado['id_surco'].isin([1, 2, 3])].copy()
    
    if len(df_suelo) > 0:
        # TARJETAS DE TRATAMIENTOS ESPACIOSAS
        c_r1, c_r2, c_r3 = st.columns(3)
        for s_id, col in [(1, c_r1), (2, c_r2), (3, c_r3)]:
            df_s = df_suelo[df_suelo['id_surco'] == s_id]
            if len(df_s) > 0:
                s_nombre = df_s['nombre_surco'].iloc[0]
                s_obj = df_s['humedad_objetivo_pct'].iloc[0]
                s_prom = df_s['valor_medido'].mean()
                s_def = int(df_s['flag_riego'].sum())
                s_pct_def = (s_def / len(df_s) * 100)
                
                with col:
                    st.markdown(f"""
                    <div class="kpi-card kpi-card-glow-{'cyan' if s_id==2 else ('emerald' if s_id==1 else 'amber')}">
                        <div>
                            <div style="font-size: 0.92rem; font-weight: 800; color: #94a3b8; text-transform: uppercase;">{s_nombre}</div>
                            <div style="font-size: 2.3rem; font-weight: 850; color: #f8fafc; margin: 6px 0;">{s_prom:.1f}% <span style="font-size: 0.95rem; color: #94a3b8; font-weight: 500;">promedio</span></div>
                            <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 4px;">Humedad Objetivo: <strong style="color: #38bdf8;">{s_obj}%</strong></div>
                        </div>
                        <div style="font-size: 0.86rem; color: #f87171; font-weight: 700; margin-top: 10px; background: rgba(239, 68, 68, 0.12); padding: 6px 10px; border-radius: 8px;">
                            Déficit de Riego: {s_def:,} hrs ({s_pct_def:.1f}%)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        st.markdown("<div class='spacer-xl'></div>", unsafe_allow_html=True)
        
        # 1. EVOLUCIÓN TEMPORAL DE HUMEDAD A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">💧 1. Evolución Temporal de la Humedad de Suelo por Tratamiento</div>
            <div class="chart-desc">Comportamiento diario de la humedad frente a las líneas de humedad objetivo de cada surco experimental.</div>
        """, unsafe_allow_html=True)
        
        df_suelo_diario = df_suelo.groupby(['fecha', 'nombre_surco'])['valor_medido'].mean().reset_index()
        fig_suelo_time = px.line(
            df_suelo_diario,
            x='fecha',
            y='valor_medido',
            color='nombre_surco',
            color_discrete_map={
                "Surco 100% Humedad": "#10b981",
                "Surco 75% Humedad": "#06b6d4",
                "Surco 50% Humedad": "#f59e0b"
            }
        )
        fig_suelo_time.add_hline(y=100, line_dash="dot", line_color="#10b981", line_width=1.8, annotation_text="Meta Surco 1 (100%)", annotation_font=dict(color="#34d399"))
        fig_suelo_time.add_hline(y=75, line_dash="dot", line_color="#06b6d4", line_width=1.8, annotation_text="Meta Surco 2 (75%)", annotation_font=dict(color="#38bdf8"))
        fig_suelo_time.add_hline(y=50, line_dash="dot", line_color="#f59e0b", line_width=1.8, annotation_text="Meta Surco 3 (50%)", annotation_font=dict(color="#fbbf24"))
        fig_suelo_time.update_layout(
            PLOTLY_THEME['layout'],
            height=540,
            xaxis_title="Fecha",
            yaxis_title="Humedad de Suelo (%)"
        )
        st.plotly_chart(fig_suelo_time, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
        
        # 2. BOX PLOT DE DISPERSIÓN A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">📦 2. Variabilidad, Cuartiles y Estabilidad Hídrica (Box Plot)</div>
            <div class="chart-desc">Distribución estadística que evidencia la consistencia del riego y la retención del sustrato entre los tratamientos.</div>
        """, unsafe_allow_html=True)
        
        fig_box = px.box(
            df_suelo,
            x='nombre_surco',
            y='valor_medido',
            color='nombre_surco',
            color_discrete_sequence=['#10b981', '#06b6d4', '#f59e0b']
        )
        fig_box.update_layout(
            PLOTLY_THEME['layout'],
            height=500,
            showlegend=False,
            xaxis_title="Tratamiento de Suelo",
            yaxis_title="Humedad Registrada (%)"
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
        
        # 3. HORAS DE RIEGO POR MES A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">⏳ 3. Horas Acumuladas con Necesidad de Riego por Mes (flag_riego = 1)</div>
            <div class="chart-desc">Horas mensuales en las que el sensor LM393 detectó déficit hídrico por debajo de la meta agronómica.</div>
        """, unsafe_allow_html=True)
        
        df_riego_mes = df_suelo.groupby(['anio', 'mes', 'nombre_mes', 'nombre_surco'])['flag_riego'].sum().reset_index()
        df_riego_mes['periodo'] = df_riego_mes['nombre_mes'] + ' ' + df_riego_mes['anio'].astype(str)
        df_riego_mes = df_riego_mes.sort_values(by=['anio', 'mes'])
        
        fig_riego_bar = px.bar(
            df_riego_mes,
            x='periodo',
            y='flag_riego',
            color='nombre_surco',
            barmode='group',
            color_discrete_map={
                "Surco 100% Humedad": "#10b981",
                "Surco 75% Humedad": "#06b6d4",
                "Surco 50% Humedad": "#f59e0b"
            }
        )
        fig_riego_bar.update_layout(
            PLOTLY_THEME['layout'],
            height=520,
            xaxis_title="Período Mensual",
            yaxis_title="Horas Totales con Déficit de Riego"
        )
        st.plotly_chart(fig_riego_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No se seleccionaron sensores de suelo en los filtros actuales.")

# =============================================================================
# TAB 5: MICROCLIMA: INTERIOR VS EXTERIOR — UNO BAJO EL OTRO
# =============================================================================
with tab5:
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;'>🌡️ Dinámica Microclimática: Interior vs Exterior</h2>", unsafe_allow_html=True)
    st.markdown(r"""
    <p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>
    Evaluación cuantitativa del efecto protector y amortiguador del invernadero, así como el diferencial térmico ($\Delta T$) y gradiente de humedad ($\Delta H$).
    </p>
    """, unsafe_allow_html=True)
    
    df_amb = df_filtrado[df_filtrado['variable_medida'].isin(['Temperatura Ambiental', 'Humedad Relativa', 'Luminosidad'])].copy()
    
    if len(df_amb) > 0:
        # 1. TEMPERATURA A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">🌡️ 1. Temperatura Ambiental: Interior vs Exterior</div>
            <div class="chart-desc">Comparativa diaria que evidencia el efecto invernadero (amortiguación en horas frías y calentamiento diurno).</div>
        """, unsafe_allow_html=True)
        
        df_temp = df_amb[df_amb['variable_medida'] == 'Temperatura Ambiental']
        if len(df_temp) > 0:
            df_temp_diaria = df_temp.groupby(['fecha', 'ubicacion'])['valor_medido'].mean().reset_index()
            fig_temp = px.line(
                df_temp_diaria,
                x='fecha',
                y='valor_medido',
                color='ubicacion',
                color_discrete_map={"Interior": "#ef4444", "Exterior": "#38bdf8"}
            )
            fig_temp.update_layout(
                PLOTLY_THEME['layout'],
                height=520,
                xaxis_title="Fecha",
                yaxis_title="Temperatura Promedio (°C)"
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
        
        # 2. HUMEDAD RELATIVA A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">💧 2. Humedad Relativa: Interior vs Exterior</div>
            <div class="chart-desc">Seguimiento de la retención de vapor de agua y condensación en el interior respecto al ambiente abierto.</div>
        """, unsafe_allow_html=True)
        
        df_hum = df_amb[df_amb['variable_medida'] == 'Humedad Relativa']
        if len(df_hum) > 0:
            df_hum_diaria = df_hum.groupby(['fecha', 'ubicacion'])['valor_medido'].mean().reset_index()
            fig_hum = px.line(
                df_hum_diaria,
                x='fecha',
                y='valor_medido',
                color='ubicacion',
                color_discrete_map={"Interior": "#10b981", "Exterior": "#818cf8"}
            )
            fig_hum.update_layout(
                PLOTLY_THEME['layout'],
                height=520,
                xaxis_title="Fecha",
                yaxis_title="Humedad Relativa (%)"
            )
            st.plotly_chart(fig_hum, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
        
        # 3. CICLO DE LUMINOSIDAD A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">☀️ 3. Ciclo Circadiano de Luminosidad (Hora 00:00 a 23:00)</div>
            <div class="chart-desc">Perfil de radiación lumínica promedio hora a hora registrado por los sensores ópticos BH1750.</div>
        """, unsafe_allow_html=True)
        
        df_lux = df_amb[df_amb['variable_medida'] == 'Luminosidad']
        if len(df_lux) > 0:
            df_lux_hora = df_lux.groupby(['hora', 'ubicacion'])['valor_medido'].mean().reset_index()
            fig_lux = px.line(
                df_lux_hora,
                x='hora',
                y='valor_medido',
                color='ubicacion',
                markers=True,
                color_discrete_map={"Interior": "#fbbf24", "Exterior": "#f59e0b"}
            )
            fig_lux.update_layout(
                PLOTLY_THEME['layout'],
                height=500,
                xaxis_title="Hora del Día (0 a 23h)",
                yaxis_title="Luminosidad Media (Lux)"
            )
            st.plotly_chart(fig_lux, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
        
        # 4. MAPA DE CALOR HORA X MES A ANCHO COMPLETO
        st.markdown("""
        <div class="chart-card">
            <div class="chart-title">🔥 4. Mapa de Calor Térmico 2D: Temperatura Interior (Hora del Día x Mes del Año)</div>
            <div class="chart-desc">Matriz completa de radiación térmica interior que permite identificar los focos de calor y los valles de enfriamiento.</div>
        """, unsafe_allow_html=True)
        
        df_heat_temp = df_amb[(df_amb['variable_medida'] == 'Temperatura Ambiental') & (df_amb['ubicacion'] == 'Interior')]
        if len(df_heat_temp) > 0:
            pivot_heat = pd.pivot_table(
                df_heat_temp,
                values='valor_medido',
                index='hora',
                columns='nombre_mes',
                aggfunc='mean'
            )
            meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            cols_orden = [m for m in meses_orden if m in pivot_heat.columns]
            if cols_orden:
                pivot_heat = pivot_heat[cols_orden]
                
            fig_heat_temp = px.imshow(
                pivot_heat,
                labels=dict(x="Mes", y="Hora del Día", color="Temperatura (°C)"),
                color_continuous_scale="Turbo"
            )
            fig_heat_temp.update_layout(
                PLOTLY_THEME['layout'],
                height=600,
                xaxis_title="Mes del Año",
                yaxis_title="Hora del Día (0 a 23h)"
            )
            st.plotly_chart(fig_heat_temp, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No hay datos ambientales disponibles con los filtros actuales.")

# =============================================================================
# TAB 6: ESQUEMA EN ESTRELLA (KIMBALL) & CATÁLOGOS
# =============================================================================
with tab6:
    st.markdown("<h2 style='font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;'>🏛️ Arquitectura del Data Warehouse — Ralph Kimball</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 24px;'>
    Estructura analítica dimensional pura en 4 tablas: 1 tabla central de hechos y 3 tablas de dimensiones con claves foráneas explícitas.
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ```
                           ┌──────────────────────────┐
                           │        dim_sensor        │ (9 Sensores físicos con umbrales)
                           ├──────────────────────────┤
                           │ id_sensor (PK)           │
                           │ codigo_variable          │
                           │ rango_min_optimo, max    │
                           └────────────┬─────────────┘
                                        │ (1:N)
      ┌──────────────────────────┐      │      ┌──────────────────────────┐
      │        dim_tiempo        │      │      │     dim_surco_suelo      │ (3 Tratamientos + N/A)
      ├──────────────────────────┤      │      ├──────────────────────────┤
      │ id_tiempo (PK)           │      │      │ id_surco (PK)            │
      │ fecha, anio, mes, hora   │      │      │ nombre_surco             │
      │ franja_horaria           │      │      │ humedad_objetivo_pct     │
      └────────────┬─────────────┘      │      └────────────┬─────────────┘
                   │ (1:N)              ▼                   │ (1:N)
                   │       ┌──────────────────────────┐     │
                   └──────►│fact_mediciones_invernad. │◄────┘ (31.977 Hechos Atómicos)
                           ├──────────────────────────┤
                           │ id_medicion (PK)         │
                           │ id_tiempo (FK)           │
                           │ id_sensor (FK)           │
                           │ id_surco (FK)            │
                           │ valor_medido             │
                           │ flag_anomalia            │
                           │ flag_riego               │
                           └──────────────────────────┘
    ```
    """)
    
    st.markdown("<div class='spacer-lg'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-card">
        <div class="chart-title">📂 Explorador de Tablas del Data Warehouse</div>
        <div class="chart-desc">Inspecciona y exporta directamente los registros y la estructura de cada tabla física del modelo.</div>
    """, unsafe_allow_html=True)
    
    tabla_sel = st.selectbox(
        "Seleccionar tabla a inspeccionar:",
        ["fact_mediciones_invernadero", "dim_tiempo", "dim_sensor", "dim_surco_suelo"]
    )
    
    df_tabla = datos_cargados[tabla_sel]
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.markdown(f"**Total de Registros:** `{len(df_tabla):,}` filas")
    with col_t2:
        st.markdown(f"**Total de Atributos:** `{len(df_tabla.columns)}` columnas")
        
    st.dataframe(df_tabla.head(150), use_container_width=True, height=400)
    
    csv_t = df_tabla.head(10000).to_csv(index=False).encode('utf-8')
    st.download_button(
        f"📥 Exportar Registros de {tabla_sel} (CSV)",
        csv_t,
        f"{tabla_sel}.csv",
        "text/csv"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# TAB 7: GESTIÓN DE USUARIOS (EXCLUSIVO ADMINISTRADOR DE BD — ACTOR UML)
# =============================================================================
if es_admin:
    with all_tabs[6]:
        render_admin_user_management()

# -----------------------------------------------------------------------------
# 6. PIE DE PÁGINA (FOOTER)
# -----------------------------------------------------------------------------
st.markdown("<div class='spacer-xl'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.88rem; padding: 24px 0 36px 0; border-top: 1px solid rgba(51, 65, 85, 0.4);">
    🌱 <strong>Semillero COTECTRONIX</strong> · Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)<br>
    Proyecto de Grado: Sistema de Monitoreo Ambiental para Invernadero Automatizado (Fase 2: ETL + OLAP)<br>
    Motor analítico potenciado con <strong>Polars & Streamlit</strong>.
</div>
""", unsafe_allow_html=True)
