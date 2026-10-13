#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
VISTAS DE INTERFAZ DE USUARIO PARA AUTENTICACIÓN Y ROLES UML
SEMILLERO DE INVESTIGACIÓN COTECTRONIX — COTECNOVA
Pantalla de Login, Recuperación de Contraseña y Panel de Usuarios
====================================================================
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any

try:
    from pag.auth_manager import (
        ROLES_UML,
        PREGUNTAS_SUGERIDAS,
        autenticar_usuario,
        obtener_pregunta_seguridad,
        restablecer_password_con_pregunta,
        crear_nuevo_usuario,
        listar_usuarios,
        cambiar_estado_usuario,
        admin_restablecer_password
    )
except ImportError:
    from auth_manager import (
        ROLES_UML,
        PREGUNTAS_SUGERIDAS,
        autenticar_usuario,
        obtener_pregunta_seguridad,
        restablecer_password_con_pregunta,
        crear_nuevo_usuario,
        listar_usuarios,
        cambiar_estado_usuario,
        admin_restablecer_password
    )


def get_role_badge_html(rol: str) -> str:
    """Retorna un badge HTML estilizado para el rol UML."""
    if "Administrador" in rol:
        return f'<span class="role-pill role-pill-admin">🟡 {rol}</span>'
    elif "Investigador" in rol:
        return f'<span class="role-pill role-pill-investigador">🟢 {rol}</span>'
    else:
        return f'<span class="role-pill role-pill-estudiante">🔵 {rol}</span>'


def render_sidebar_user_profile() -> None:
    """Muestra en la barra lateral el perfil del usuario autenticado y el botón de logout."""
    current_user = st.session_state.get('current_user')
    if not current_user:
        return

    rol = current_user.get('rol', 'Investigador / Docente')
    nombre = current_user.get('nombre_completo', 'Usuario')
    username = current_user.get('username', 'user')
    semillero = current_user.get('semillero', 'COTECTRONIX')

    icono = "🟡" if "Administrador" in rol else ("🟢" if "Investigador" in rol else "🔵")

    st.sidebar.markdown(f"""
    <div class="user-profile-sidebar">
        <div class="user-profile-header">
            <div class="user-avatar">{icono}</div>
            <div style="overflow: hidden;">
                <div style="font-weight: 800; font-size: 0.96rem; color: #f8fafc; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{nombre}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; font-family: monospace;">@{username}</div>
            </div>
        </div>
        <div style="margin-bottom: 8px;">
            {get_role_badge_html(rol)}
        </div>
        <div style="font-size: 0.76rem; color: #64748b; margin-top: 4px;">
            🏛️ Semillero: <strong style="color: #cbd5e1;">{semillero}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()


def render_login_view() -> None:
    """Renderiza la vista principal de inicio de sesión y recuperación de contraseña."""
    # Contenedor centrado
    st.markdown("""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
        <span style="font-size: 3.5rem;">🌿</span>
        <h1 style="font-size: 2.2rem; font-weight: 850; background: linear-gradient(135deg, #34d399 0%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 4px 0 2px 0;">
            Invernadero Inteligente COTECTRONIX
        </h1>
        <p style="color: #94a3b8; font-size: 1.05rem; margin-top: 4px;">
            Plataforma Analítica Multidimensional OLAP · COTECNOVA (Fase 2)
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([1, 2.2, 1])

    with col_centro:
        tab_login, tab_recuperar, tab_ayuda = st.tabs([
            "🔐 Iniciar Sesión",
            "❓ Recuperar Contraseña",
            "👥 Actores y Cuentas"
        ])

        # -------------------------------------------------------------
        # 1. PESTAÑA DE INICIAR SESIÓN
        # -------------------------------------------------------------
        with tab_login:
            st.markdown("""
            <div style="padding: 10px 0 16px 0;">
                <h3 style="margin: 0; font-size: 1.25rem; color: #f8fafc; font-weight: 700;">Acceso a la Plataforma</h3>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #94a3b8;">
                    Ingresa tus credenciales asignadas para consultar el tablero analítico.
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_login", clear_on_submit=False):
                usuario_input = st.text_input(
                    "👤 Nombre de usuario o identificador:",
                    placeholder="Ej. admin o investigador",
                    key="login_user"
                )
                password_input = st.text_input(
                    "🔑 Contraseña:",
                    type="password",
                    placeholder="••••••••",
                    key="login_pwd"
                )

                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                btn_login = st.form_submit_button(
                    "🚀 Ingresar al Tablero Analítico",
                    use_container_width=True,
                    type="primary"
                )

                if btn_login:
                    exito, datos_u, mensaje = autenticar_usuario(usuario_input, password_input)
                    if exito:
                        st.session_state.logged_in = True
                        st.session_state.current_user = datos_u
                        st.toast(f"¡Bienvenido(a), {datos_u['nombre_completo']}!", icon="🌿")
                        st.rerun()
                    else:
                        st.error(f"❌ {mensaje}")

        # -------------------------------------------------------------
        # 2. PESTAÑA DE RECUPERACIÓN DE CONTRASEÑA
        # -------------------------------------------------------------
        with tab_recuperar:
            st.markdown("""
            <div style="padding: 10px 0 14px 0;">
                <h3 style="margin: 0; font-size: 1.25rem; color: #f8fafc; font-weight: 700;">Recuperación de Contraseña</h3>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #94a3b8;">
                    Recupera tu acceso respondiendo a la pregunta de seguridad privada registrada en tu cuenta.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Estado para manejar la búsqueda del usuario
            if "recuperar_user_valido" not in st.session_state:
                st.session_state.recuperar_user_valido = None
                st.session_state.recuperar_pregunta = None

            col_u1, col_u2 = st.columns([2.5, 1.2])
            with col_u1:
                user_buscar = st.text_input(
                    "Usuario a recuperar:",
                    placeholder="Ej. investigador o admin",
                    key="input_user_recuperar"
                )
            with col_u2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                btn_buscar = st.button("🔍 Validar", use_container_width=True)

            if btn_buscar:
                if user_buscar.strip():
                    ok, preg, msg = obtener_pregunta_seguridad(user_buscar)
                    if ok:
                        st.session_state.recuperar_user_valido = user_buscar.strip().lower()
                        st.session_state.recuperar_pregunta = preg
                    else:
                        st.session_state.recuperar_user_valido = None
                        st.session_state.recuperar_pregunta = None
                        st.error(f"⚠️ {msg}")
                else:
                    st.warning("Escribe el nombre de usuario.")

            if st.session_state.recuperar_user_valido and st.session_state.recuperar_pregunta:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(52, 211, 153, 0.35); border-radius: 12px; padding: 14px; margin: 12px 0;">
                    <div style="font-size: 0.78rem; color: #34d399; font-weight: 700; text-transform: uppercase;">Pregunta Secreta Registrada</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                        ❓ {st.session_state.recuperar_pregunta}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.form("form_cambiar_pwd_pregunta"):
                    respuesta_input = st.text_input(
                        "✍️ Tu respuesta secreta:",
                        placeholder="Escribe la respuesta confidencial",
                        help="No distingue mayúsculas de minúsculas ni tildes.",
                        type="password"
                    )
                    nueva_pwd_input = st.text_input(
                        "🔒 Nueva contraseña:",
                        type="password",
                        placeholder="Mínimo 6 caracteres"
                    )
                    confirma_pwd_input = st.text_input(
                        "🔒 Confirma la nueva contraseña:",
                        type="password",
                        placeholder="Repite la contraseña"
                    )

                    btn_cambiar = st.form_submit_button(
                        "✨ Restablecer Contraseña e Ingresar",
                        use_container_width=True,
                        type="primary"
                    )

                    if btn_cambiar:
                        if nueva_pwd_input != confirma_pwd_input:
                            st.error("❌ Las dos contraseñas ingresadas no coinciden.")
                        else:
                            ok_cambio, msg_cambio = restablecer_password_con_pregunta(
                                st.session_state.recuperar_user_valido,
                                respuesta_input,
                                nueva_pwd_input
                            )
                            if ok_cambio:
                                st.success(f"✅ {msg_cambio}")
                                st.info("👉 Ahora dirígete a la pestaña **🔐 Iniciar Sesión** con tu nueva contraseña.")
                                st.session_state.recuperar_user_valido = None
                                st.session_state.recuperar_pregunta = None
                            else:
                                st.error(f"❌ {msg_cambio}")

        # -------------------------------------------------------------
        # 3. PESTAÑA DE AYUDA Y ACTORES UML
        # -------------------------------------------------------------
        with tab_ayuda:
            st.markdown("""
            <div style="padding: 10px 0 14px 0;">
                <h3 style="margin: 0; font-size: 1.25rem; color: #f8fafc; font-weight: 700;">Actores del Sistema (Diagramas UML)</h3>
                <p style="margin: 4px 0 14px 0; font-size: 0.88rem; color: #94a3b8;">
                    Cuentas precargadas correspondientes a los actores modelados en la Fase 2:
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="demo-card-item" style="border-left: 3px solid #f59e0b;">
                <div style="font-weight: 700; color: #fbbf24;">🟡 Administrador de BD (Actor UML)</div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin: 3px 0;">Capacidad de crear usuarios, auditar roles, supervisar ETL y base relacional.</div>
                <div style="font-family: monospace; font-size: 0.85rem; color: #e2e8f0; margin-top: 4px;">
                    Usuario: <strong>admin</strong> | Clave: <strong>admin123</strong><br>
                    Pregunta: <em>¿Cuál es el nombre del semillero de investigación?</em><br>
                    Respuesta: <strong>cotectronix</strong>
                </div>
            </div>

            <div class="demo-card-item" style="border-left: 3px solid #10b981; margin-top: 10px;">
                <div style="font-weight: 700; color: #34d399;">🟢 Investigador / Docente (Actor UML)</div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin: 3px 0;">Acceso a tableros analíticos multidimensionales, detección de anomalías y riego.</div>
                <div style="font-family: monospace; font-size: 0.85rem; color: #e2e8f0; margin-top: 4px;">
                    Usuario: <strong>investigador</strong> | Clave: <strong>investigador123</strong><br>
                    Pregunta: <em>¿Cuál es la institución universitaria del proyecto?</em><br>
                    Respuesta: <strong>cotecnova</strong>
                </div>
            </div>

            <div class="demo-card-item" style="border-left: 3px solid #06b6d4; margin-top: 10px;">
                <div style="font-weight: 700; color: #38bdf8;">🔵 Estudiante / Semillerista</div>
                <div style="font-size: 0.82rem; color: #94a3b8; margin: 3px 0;">Exploración de datos del invernadero y soporte de campo.</div>
                <div style="font-family: monospace; font-size: 0.85rem; color: #e2e8f0; margin-top: 4px;">
                    Usuario: <strong>estudiante</strong> | Clave: <strong>estudiante123</strong><br>
                    Pregunta: <em>¿Cuál es el nombre del semillero de investigación?</em><br>
                    Respuesta: <strong>cotectronix</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_admin_user_management() -> None:
    """Renderiza el panel de gestión y creación de usuarios exclusivo para el Administrador de BD."""
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-size: 1.6rem; font-weight: 800; color: #f8fafc; margin-bottom: 6px;">
            👥 Gestión y Creación de Usuarios (Panel de Administrador)
        </h2>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0;">
            Como <strong>Administrador de BD</strong>, tienes los privilegios para crear nuevas cuentas, asignar roles basados en el modelo UML y administrar el acceso al tablero analítico.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_crear, tab_listar = st.tabs([
        "➕ Registrar Nuevo Usuario",
        "📋 Directorio de Usuarios del Sistema"
    ])

    # -------------------------------------------------------------
    # 1. FORMULARIO PARA CREAR NUEVO USUARIO
    # -------------------------------------------------------------
    with tab_crear:
        st.markdown("#### ✨ Datos del Nuevo Usuario")
        with st.form("form_crear_usuario", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nuevo_username = st.text_input(
                    "👤 Nombre de usuario (Login ID):",
                    placeholder="Ej. maria_investigadora"
                )
                nuevo_nombre = st.text_input(
                    "🏷️ Nombre completo:",
                    placeholder="Ej. Dra. María Rodríguez"
                )
                nuevo_rol = st.selectbox(
                    "🎭 Rol del Actor UML:",
                    options=ROLES_UML,
                    index=1,
                    help="Determina las atribuciones y nivel de acceso en la plataforma."
                )

            with col2:
                nueva_clave = st.text_input(
                    "🔑 Contraseña inicial:",
                    type="password",
                    placeholder="Mínimo 6 caracteres"
                )
                opcion_pregunta = st.selectbox(
                    "❓ Seleccionar pregunta secreta de seguridad:",
                    options=PREGUNTAS_SUGERIDAS + ["Personalizada (Escribir propia)..."]
                )
                if opcion_pregunta.startswith("Personalizada"):
                    pregunta_final = st.text_input("Escribe la pregunta personalizada:")
                else:
                    pregunta_final = opcion_pregunta

                nueva_respuesta = st.text_input(
                    "✍️ Respuesta secreta (para recuperar contraseña):",
                    placeholder="Respuesta confidencial conocida por el usuario"
                )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            btn_guardar_usuario = st.form_submit_button(
                "💾 Guardar y Crear Usuario",
                use_container_width=True,
                type="primary"
            )

            if btn_guardar_usuario:
                ok, msg = crear_nuevo_usuario(
                    username=nuevo_username,
                    nombre_completo=nuevo_nombre,
                    password=nueva_clave,
                    rol=nuevo_rol,
                    pregunta=pregunta_final,
                    respuesta=nueva_respuesta
                )
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

    # -------------------------------------------------------------
    # 2. LISTA DE USUARIOS Y CONTROL DE ESTADOS
    # -------------------------------------------------------------
    with tab_listar:
        st.markdown("#### 📑 Cuentas Registradas en el Sistema")
        usuarios = listar_usuarios()
        
        if usuarios:
            df_usuarios = pd.DataFrame(usuarios)
            df_mostrar = df_usuarios[['id_usuario', 'username', 'nombre_completo', 'rol', 'semillero', 'activo', 'ultimo_acceso']].copy()
            df_mostrar.columns = ['ID', 'Usuario', 'Nombre Completo', 'Rol UML', 'Semillero', 'Activo', 'Último Acceso']
            
            # Formatear booleano
            df_mostrar['Activo'] = df_mostrar['Activo'].apply(lambda x: '🟢 Activo' if x == 1 else '🔴 Inactivo')
            df_mostrar['Último Acceso'] = df_mostrar['Último Acceso'].fillna('Sin accesos aún')

            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 🛠️ Acciones de Mantenimiento por Usuario")
            
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                with st.expander("🔄 Activar / Desactivar Usuario"):
                    user_to_toggle = st.selectbox(
                        "Seleccionar usuario:",
                        options=[u['username'] for u in usuarios if u['username'] != 'admin'],
                        key="select_user_toggle"
                    )
                    usuario_sel_obj = next((u for u in usuarios if u['username'] == user_to_toggle), None)
                    estado_actual = usuario_sel_obj['activo'] == 1 if usuario_sel_obj else True
                    
                    nuevo_estado = st.radio(
                        f"Estado para @{user_to_toggle}:",
                        ["Habilitado / Activo", "Deshabilitado / Inactivo"],
                        index=0 if estado_actual else 1
                    )
                    if st.button("Guardar Cambio de Estado", use_container_width=True):
                        ok_t, msg_t = cambiar_estado_usuario(user_to_toggle, nuevo_estado.startswith("Habilitado"))
                        if ok_t:
                            st.success(f"✅ {msg_t}")
                            st.rerun()
                        else:
                            st.error(f"❌ {msg_t}")

            with col_act2:
                with st.expander("🔑 Restablecer Contraseña Directamente (Emergencia)"):
                    user_to_reset = st.selectbox(
                        "Seleccionar cuenta:",
                        options=[u['username'] for u in usuarios],
                        key="select_user_reset_admin"
                    )
                    admin_new_pwd = st.text_input(
                        "Nueva contraseña para el usuario:",
                        type="password",
                        key="admin_new_pwd_input"
                    )
                    if st.button("Actualizar Contraseña de Usuario", use_container_width=True):
                        ok_r, msg_r = admin_restablecer_password(user_to_reset, admin_new_pwd)
                        if ok_r:
                            st.success(f"✅ {msg_r}")
                        else:
                            st.error(f"❌ {msg_r}")
        else:
            st.info("No hay usuarios registrados.")
