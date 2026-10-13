# 🌿 Aplicación Web Analítica OLAP — Invernadero COTECNOVA (Fase 2)

**Semillero de Investigación:** COTECTRONIX  
**Institución:** Corporación de Estudios Tecnológicos del Norte del Valle (COTECNOVA)  
**Tecnología:** Python 3 + Streamlit + Plotly + Polars  
**Metodología:** Ralph Kimball (Modelo Dimensional / Esquema en Estrella)  

---

## 🚀 1. Formas de Ejecución

Puedes iniciar la plataforma analítica de cualquiera de las siguientes 3 maneras:

### Opción 1: Mediante comando directo de Streamlit
```bash
streamlit run pag/app.py
```

### Opción 2: Mediante script Python
```bash
python run_dashboard.py
```

### Opción 3: Doble clic en Windows
Ejecuta el archivo [`pag/iniciar_dashboard.bat`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/iniciar_dashboard.bat).

> La aplicación abrirá automáticamente en tu navegador predeterminado en: **`http://localhost:8501`**

---

## ⚙️ 2. Configuración de la Página (`st.set_page_config`)

La aplicación inicia con la configuración global requerida por Streamlit:

```python
st.set_page_config(
    page_title="Invernadero OLAP · COTECTRONIX",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/calitosxd/fase1semillero',
        'About': "### Sistema de Monitoreo Ambiental e Inteligencia de Datos - Fase 2\nSemillero COTECTRONIX — COTECNOVA."
    }
)
```

- **`layout="wide"`**: Aprovecha el ancho completo de la pantalla para renderizar tableros analíticos multidimensionales y matrices térmicas de alta densidad.
- **`initial_sidebar_state="expanded"`**: Mantiene desplegado el panel lateral con los filtros dimensionales de corte y selección (Slice & Dice).
- **Diseño Glassmorphism Premium**: Inyección de CSS moderno con tipografía Google *Plus Jakarta Sans*, tarjetas de KPI con bordes luminosos y paleta optimizada esmeralda-cian.

---

## 🏛️ 3. Arquitectura de Datos y Motores de Consulta

La aplicación implementa soporte **dual** para garantizar disponibilidad inmediata y flexibilidad:

1. **⚡ Motor In-Memory de Ultra-Alta Velocidad (Polars - Recomendado):**
   - Transforma y ensambla las 31.977 mediciones atómicas y las 3 dimensiones en menos de **160 milisegundos**.
   - Almacena en memoria bajo `@st.cache_data`.
   - **Cero configuración requerida**: Funciona de inmediato sin necesidad de ingresar contraseñas de bases de datos.

2. **🐬 Motor Relacional MySQL (`invernadero_olap_fase2`):**
   - Permite ingresar credenciales en el panel lateral (Host, Puerto, Usuario, Contraseña).
   - Valida la conexión y consulta las tablas físicas creadas con el script `invernadero_olap_fase2.sql`.

---

## 📊 4. Módulos y Pestañas Analíticas

| Pestaña | Funcionalidad | Requerimiento Asociado |
|---|---|---|
| **1. Resumen Ejecutivo** | 4 KPIs en tiempo real (Capturas, Mediciones, Anomalías %, Horas Riego). Evolución mensual y estado de los 9 sensores con sus rangos agronómicos. | CU-08, CU-12 |
| **2. Cubo Multidimensional (OLAP)** | **Rotación Pivot Dinámica** cruzando filas, columnas y métricas con heatmap interactivo y descarga CSV. **Jerarquías Temporales (Roll-up / Drill-down)** de Año a Hora. | RF-10, CU-08 |
| **3. Detección de Anomalías** | Ranking de anomalías por sensor, concentración por franja horaria e inspección detallada de dispersión temporal con bandas de alerta y rangos óptimos. | RF-07, CU-09 |
| **4. Agronomía y Riego** | Evaluación de los tratamientos al 100%, 75% y 50% de humedad. Horas acumuladas de déficit de riego (`flag_riego = 1`), gráficos de dispersión (Box Plots) y series temporales. | RF-08, CU-10, CU-11 |
| **5. Microclima (Int vs Ext)** | Diferencial térmico ($\Delta T$) y efecto invernadero. Diferencial de humedad ($\Delta H$). Ciclo circadiano de luminosidad promedio (0 a 23h). Mapa de calor de temperatura interior (Hora x Mes). | RF-10 |
| **6. Esquema en Estrella (Kimball)** | Visualización conceptual de las 4 tablas con sus claves primarias y foráneas. Explorador interactivo de datos con paginación y exportación de cada dimensión. | RNF-01, CU-13 |
| **7. Gestión de Usuarios (Exclusivo Admin)** | **Panel del Administrador de BD:** Creación de nuevos usuarios con rol UML, definición de preguntas secretas, auditoría de accesos, habilitación/deshabilitación y restablecimiento de contraseñas. | Actores UML, Seguridad |

---

## 🔐 5. Módulo de Seguridad y Actores UML

La plataforma implementa control de acceso basado en roles (**RBAC**) y persistencia de usuarios:

### Actores modelados en los Diagramas UML:
1. **🟡 Administrador de BD (`admin`):**
   - Gestión integral de usuarios (creación, cambio de rol, estado y restablecimiento de claves).
   - Acceso al Data Warehouse, esquemas dimensionales y tableros analíticos.
2. **🟢 Investigador / Docente (`investigador`):**
   - Acceso a consultas analíticas multidimensionales (OLAP), detección de anomalías y riego.
3. **🔵 Estudiante / Semillerista (`estudiante`):**
   - Consultas operativas y soporte de campo del semillero COTECTRONIX.

### Recuperación de Contraseña sin Complicaciones:
- Cada cuenta almacena una **pregunta de seguridad confidencial** configurada al crearse.
- Si el usuario olvida su contraseña, ingresa su identificador, el sistema le presenta su pregunta secreta y, al responderla correctamente, puede definir inmediatamente su nueva clave.

---

## 📂 6. Estructura de Archivos del Módulo

- [`pag/app.py`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/app.py): Aplicación principal del tablero Streamlit con barrera de autenticación.
- [`pag/auth_manager.py`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/auth_manager.py): Gestor backend de usuarios, hashing SHA-256 con sal, persistencia SQLite y validaciones.
- [`pag/auth_ui.py`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/auth_ui.py): Componentes de UI para Login, Recuperación por pregunta secreta y Gestión de Usuarios para el Admin.
- [`pag/data_loader.py`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/data_loader.py): Cargador de datos optimizado con Polars y conector opcional MySQL.
- [`pag/styles.py`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/styles.py): Estilos CSS modernos, tarjetas KPI, badges de roles y tokens visuales.
- [`database/tabla_usuarios_mysql.sql`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/database/tabla_usuarios_mysql.sql): Script DDL compatible con MySQL/MariaDB para usuarios y roles.
- [`run_dashboard.py`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/run_dashboard.py): Lanzador rápido desde la raíz del repositorio.
- [`iniciar_dashboard.bat`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/iniciar_dashboard.bat): Lanzador por lotes para Windows desde la raíz del proyecto.
- [`pag/iniciar_dashboard.bat`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/pag/iniciar_dashboard.bat): Lanzador por lotes para Windows desde la carpeta `pag/`.
