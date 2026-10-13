#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estilos CSS y Helpers de Diseño para Invernadero OLAP - COTECTRONIX
Diseño moderno, paleta esmeralda-cian, glassmorphism, tipografía Inter y espaciado amplio.
"""

def get_custom_css() -> str:
    return """
    <style>
        /* Importar fuente Google Inter */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Espaciado de contenedor principal de Streamlit */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 4rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }

        /* Banner principal del Header */
        .hero-header {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.1) 50%, rgba(15, 23, 42, 0.4) 100%);
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: 16px;
            padding: 28px 34px;
            margin-bottom: 32px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .hero-title {
            font-size: 2.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #34d399 0%, #38bdf8 60%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.5px;
        }

        .hero-subtitle {
            color: #94a3b8;
            font-size: 1.05rem;
            margin-top: 8px;
            margin-bottom: 0;
            line-height: 1.5;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(16, 185, 129, 0.18);
            border: 1px solid rgba(52, 211, 153, 0.4);
            color: #34d399;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }

        /* Tarjetas de Métricas KPI Glassmorphism con gran espacio */
        .kpi-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(51, 65, 85, 0.6);
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 170px;
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: rgba(52, 211, 153, 0.5);
            box-shadow: 0 10px 35px rgba(16, 185, 129, 0.18);
        }

        .kpi-card-glow-emerald::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #10b981, #06b6d4);
        }

        .kpi-card-glow-cyan::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #06b6d4, #3b82f6);
        }

        .kpi-card-glow-amber::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #f59e0b, #ef4444);
        }

        .kpi-card-glow-purple::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #8b5cf6, #ec4899);
        }

        .kpi-icon {
            font-size: 2.2rem;
            margin-bottom: 10px;
        }

        .kpi-label {
            color: #94a3b8;
            font-size: 0.95rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.9px;
            margin-bottom: 6px;
        }

        .kpi-value {
            font-size: 2.6rem;
            font-weight: 850;
            color: #f8fafc;
            margin-bottom: 6px;
            font-feature-settings: "tnum";
            line-height: 1.1;
        }

        .kpi-delta {
            font-size: 0.92rem;
            color: #64748b;
            font-weight: 600;
            margin-top: 4px;
        }

        .kpi-delta-positive {
            color: #34d399;
        }

        .kpi-delta-warning {
            color: #fbbf24;
        }

        .kpi-delta-alert {
            color: #f87171;
        }

        /* Contenedor espacioso para cada gráfico analítico */
        .chart-card {
            background: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(51, 65, 85, 0.55);
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 36px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        }

        .chart-title {
            font-size: 1.35rem;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 4px;
            letter-spacing: -0.3px;
        }

        .chart-desc {
            font-size: 0.92rem;
            color: #94a3b8;
            margin-bottom: 20px;
            line-height: 1.4;
        }

        /* Espaciadores */
        .spacer-xl {
            height: 36px;
        }

        .spacer-lg {
            height: 24px;
        }

        /* Estilo para pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: rgba(15, 23, 42, 0.5);
            padding: 10px 14px;
            border-radius: 14px;
            border: 1px solid rgba(51, 65, 85, 0.5);
            margin-bottom: 28px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 10px 22px;
            font-size: 0.98rem;
            font-weight: 600;
            color: #94a3b8;
            border-radius: 10px;
            border: none;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #f1f5f9;
            background: rgba(51, 65, 85, 0.4);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.28) 0%, rgba(6, 182, 212, 0.28) 100%) !important;
            color: #34d399 !important;
            border: 1px solid rgba(52, 211, 153, 0.45) !important;
        }

        /* Estilo para paneles de información */
        .info-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(71, 85, 105, 0.5);
            border-radius: 8px;
            font-size: 0.88rem;
            color: #cbd5e1;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Callout decorado */
        .callout-box {
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid #10b981;
            padding: 18px 24px;
            border-radius: 0 12px 12px 0;
            margin: 24px 0;
            color: #e2e8f0;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* =========================================================================
           ESTILOS DEL MÓDULO DE AUTENTICACIÓN Y ROLES UML
           ========================================================================= */
        .auth-container {
            max-width: 520px;
            margin: 0 auto;
            padding: 10px;
        }

        .auth-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid rgba(52, 211, 153, 0.25);
            border-radius: 20px;
            padding: 36px 32px;
            box-shadow: 0 20px 45px rgba(0, 0, 0, 0.5), 0 0 35px rgba(16, 185, 129, 0.12);
            backdrop-filter: blur(16px);
            margin-bottom: 24px;
        }

        .auth-header {
            text-align: center;
            margin-bottom: 24px;
        }

        .auth-title {
            font-size: 1.85rem;
            font-weight: 800;
            background: linear-gradient(135deg, #34d399 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 8px 0 4px 0;
        }

        .auth-subtitle {
            color: #94a3b8;
            font-size: 0.92rem;
            margin: 0;
        }

        .role-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .role-pill-admin {
            background: rgba(245, 158, 11, 0.18);
            border: 1px solid rgba(245, 158, 11, 0.45);
            color: #fbbf24;
        }

        .role-pill-investigador {
            background: rgba(16, 185, 129, 0.18);
            border: 1px solid rgba(16, 185, 129, 0.45);
            color: #34d399;
        }

        .role-pill-estudiante {
            background: rgba(6, 182, 212, 0.18);
            border: 1px solid rgba(6, 182, 212, 0.45);
            color: #38bdf8;
        }

        .user-profile-sidebar {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(51, 65, 85, 0.7);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 20px;
        }

        .user-profile-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }

        .user-avatar {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(52, 211, 153, 0.35);
        }

        .demo-card-item {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(51, 65, 85, 0.6);
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 8px;
            font-size: 0.85rem;
            color: #cbd5e1;
        }
    </style>
    """

def render_kpi_card(icon: str, label: str, value: str, delta: str, glow_type: str = "emerald", delta_class: str = "positive") -> str:
    """Retorna el código HTML para una tarjeta KPI con animación suave y estilo glass."""
    return f"""
    <div class="kpi-card kpi-card-glow-{glow_type}">
        <div>
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        <div class="kpi-delta kpi-delta-{delta_class}">{delta}</div>
    </div>
    """
