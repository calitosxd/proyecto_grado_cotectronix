# 📐 Diagramas UML — Sistema de Monitoreo Ambiental Fase 2 (ETL + OLAP)
## Semillero COTECTRONIX — COTECNOVA

Se generaron **4 diagramas UML en formato Draw.io** (`.drawio`) editables directamente en [draw.io / diagrams.net](https://app.diagrams.net/).

---

## 📂 Archivos Generados

Los archivos se encuentran en la carpeta `diagramas_uml` de tu proyecto:

| # | Diagrama | Archivo | Descripción |
|---|----------|---------|-------------|
| 1 | **Casos de Uso** | [`01_casos_de_uso.drawio`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/diagramas_uml/01_casos_de_uso.drawio) | 4 actores, 13 casos de uso, relaciones `«include»` y `«extend»` |
| 2 | **Clases (Usuarios / Entidades)** | [`02_diagrama_clases.drawio`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/diagramas_uml/02_diagrama_clases.drawio) | Actores, componente ETL, modelo dimensional (Kimball), artefactos |
| 3 | **Estados** | [`03_diagrama_estados.drawio`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/diagramas_uml/03_diagrama_estados.drawio) | 11 estados del proceso ETL con transiciones y caminos de error |
| 4 | **Actividades** | [`04_diagrama_actividades.drawio`](file:///c:/Users/LENOVO/Downloads/proyecto_grado_cotectronix/diagramas_uml/04_diagrama_actividades.drawio) | Flujo completo con swimlanes, fork/join paralelo y decisiones |

---

## 🎭 Diagrama 1: Casos de Uso

### Actores identificados

| Actor | Tipo | Color |
|-------|------|-------|
| **Investigador / Docente** | Primario | 🟢 Verde |
| **Administrador de BD** | Primario | 🟡 Amarillo |
| **Script ETL (etl_polars.py)** | Sistema | 🔴 Rojo |
| **Sistema IoT Fase 1** | Externo | 🟣 Púrpura |

### Casos de uso

| ID | Caso de Uso | Actor(es) | RF asociado |
|----|-------------|-----------|-------------|
| CU-01 | Extraer Dataset Histórico CSV | Script ETL, IoT Fase 1 | RF-01 |
| CU-02 | Validar y Limpiar Datos | Script ETL | RF-02 |
| CU-03 | Transformar Datos (Pivoteo Vertical) | Script ETL | RF-03 |
| CU-04 | Construir Dimensiones OLAP | Script ETL | RF-04, RF-05, RF-06 |
| CU-05 | Calcular Indicadores Agronómicos | Script ETL | RF-07, RF-08 |
| CU-06 | Generar Script SQL Portable | Script ETL | RF-11 |
| CU-07 | Importar BD OLAP en MySQL | Admin BD | — |
| CU-08 | Consultar Analítica Multidimensional | Investigador | RF-10 |
| CU-09 | Analizar Anomalías por Sensor/Período | Investigador | RF-07 |
| CU-10 | Evaluar Necesidad de Riego por Surco | Investigador | RF-08 |
| CU-11 | Comparar Tratamientos Agronómicos | Investigador | RF-10 |
| CU-12 | Ejecutar Proceso ETL Completo | Admin BD | RF-01–RF-09 |
| CU-13 | Visualizar Esquema Estrella en BI | Admin BD | RNF-06 |

### Relaciones clave
- **CU-12 «include»** → CU-01 a CU-06 (el ETL completo incluye todos los subprocesos)
- **CU-08 «include»** → CU-09, CU-10 (la consulta analítica incluye análisis de anomalías y riego)
- **CU-11 «extend»** → CU-08 (comparar tratamientos extiende la consulta analítica)
- **CU-13 «extend»** → CU-07 (visualización del esquema extiende la importación)

---

## 🏗️ Diagrama 2: Clases (Usuarios y Entidades)

### Clases modeladas

| Estereotipo | Clase | Atributos clave |
|-------------|-------|-----------------|
| `«actor»` | Investigador / Docente | nombre, rol, semillero |
| `«actor»` | Administrador de BD | nombre, herramientaBI |
| `«component»` | MotorETL (etl_polars.py) | csv_path, sensores_meta, batch_size |
| `«dimension»` | dim_tiempo | id_tiempo (PK), fecha_hora, franja_horaria, 13 atributos |
| `«dimension»` | dim_sensor | id_sensor (PK), codigo_variable (UNIQUE), rangos, umbrales |
| `«dimension»` | dim_surco_suelo | id_surco (PK), humedad_objetivo_pct, tratamiento |
| `«fact table»` | fact_mediciones_invernadero | id_medicion (PK), 3 FK, valor_medido, flags |
| `«dataSource»` | Dataset CSV Fase 1 | 3,553 filas, 11 columnas, separador `;` |
| `«artifact»` | invernadero_olap_fase2.sql | ~2.4 MB, DDL+DML, utf8mb4 |
| `«infrastructure»` | MySQL 8+ / MariaDB 10.4+ | InnoDB, XAMPP |

### Relaciones FK (Esquema Estrella Kimball)
- `fact_mediciones_invernadero` **N:1** → `dim_tiempo` (via `id_tiempo`)
- `fact_mediciones_invernadero` **N:1** → `dim_sensor` (via `id_sensor`)
- `fact_mediciones_invernadero` **N:1** → `dim_surco_suelo` (via `id_surco`)

---

## 🔄 Diagrama 3: Estados

### Flujo de estados del proceso ETL

```
[●] → Inactivo → Extrayendo CSV → Validando Datos → ─┬─ [Error Validación] → [✖]
                                                       │
                                                       ▼
                                    Construyendo Dimensiones → Pivoteando Mediciones
                                                       │          │
                                                       │     [Error Integridad]
                                                       ▼
                                    Calculando Anomalías → Calculando Riego
                                                       │
                                                       ▼
                               Ensamblando Tabla Hechos → Generando SQL → ETL Completado
                                                                               │
                                                                      BD OLAP Importada → [◉]
```

---

## 🏃 Diagrama 4: Actividades

### Swimlanes (carriles de responsabilidad)

| Carril | Responsable | Actividades |
|--------|-------------|-------------|
| 🟣 Sistema IoT Fase 1 | Hardware ESP32 + sensores | Generar y exportar CSV histórico |
| 🔵 Motor ETL (Polars) | `etl_polars.py` | Leer CSV, validar, construir dimensiones, pivotear, calcular flags, ensamblar, generar SQL |
| 🟡 Administrador BD | Persona / phpMyAdmin | Ejecutar comando ETL, importar SQL, verificar esquema estrella |

### Elementos de modelado
- **2 decisiones** (rombos): ¿CSV existe?, ¿Validación OK?
- **1 fork/join paralelo** (barras): dim_tiempo ‖ dim_sensor+dim_surco ‖ pivoteo
- **2 caminos de error** (rojo): FileNotFoundError, ValueError
- **2 notas de objeto**: archivo CSV y script SQL generado

---

## 🚀 Cómo abrir los diagramas en Draw.io / Diagrams.net

1. Abre [app.diagrams.net](https://app.diagrams.net/) en el navegador.
2. Haz clic en **"Abrir archivo existente"** (Open Existing Diagram).
3. Selecciona cualquiera de los archivos `.drawio` de la carpeta `diagramas_uml`.
4. Si deseas guardarlos en imagen o PDF, ve a `Archivo → Exportar como` (`PNG`, `SVG`, `PDF`).
