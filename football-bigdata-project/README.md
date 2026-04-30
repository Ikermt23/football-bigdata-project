# ⚽ Football Players Stats 2024-2025 — Proyecto Final Big Data

> **Especialidad Big Data e IA** · España · Curso 2024-2025  
> Dataset: [Football Players Stats 2024-2025 — Kaggle/FBref](https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025)

---

## 📋 Índice

- [Resumen / Abstract](#-resumen--abstract)
- [Introducción](#-introducción)
- [1. Explicación y detalles de los datos](#1-explicación-y-detalles-de-los-datos)
- [2. Selección e Integración de Datasets](#2-selección-e-integración-de-datasets)
- [3. Metodología CRISP-DM](#3-metodología-crisp-dm)
- [4. Herramientas y Tecnologías](#4-herramientas-y-tecnologías)
- [5. Implementación Práctica](#5-implementación-práctica)
- [6. Resultados y Visualizaciones](#6-resultados-y-visualizaciones)
- [Conclusiones](#-conclusiones)
- [Bibliografía](#-bibliografía)
- [Estructura del repositorio](#-estructura-del-repositorio)

---

## 🧾 Resumen / Abstract

Este proyecto aplica técnicas de Big Data e Inteligencia Artificial al análisis del rendimiento de **1.057 jugadores de fútbol profesional** de las 5 grandes ligas europeas durante la temporada 2024-2025. Utilizando el dataset *Football Players Stats* (FBref / Kaggle), se construye un pipeline completo que abarca desde la exploración y limpieza de datos hasta la aplicación de modelos de machine learning (regresión lineal, Random Forest, K-Means, árbol de decisión) y la visualización interactiva en Power BI.

Los principales hallazgos incluyen: La Liga presenta la mayor producción ofensiva media (9,93 G+A por jugador), el 56% de los jugadores supera sus expected goals (xG), y el modelo Random Forest alcanza un R² de 0,45 en la predicción de G+A, superando la regresión lineal (R²=0,35). El clustering K-Means identifica 3 perfiles diferenciados: delanteros goleadores, mediocampistas creativos y defensores.

---

## 📖 Introducción

El fútbol moderno ha experimentado una revolución analítica impulsada por métricas avanzadas como los *Expected Goals* (xG) y los pases progresivos. Este proyecto nace de la pregunta: **¿hasta qué punto las estadísticas avanzadas predicen el rendimiento real de un jugador?**

Para responderla, se integran herramientas de análisis de datos (Python, SQL), modelos de machine learning y dashboards interactivos (Power BI), siguiendo la metodología estándar CRISP-DM y aplicando los conocimientos adquiridos en las asignaturas de Sistemas en Big Data y Aplicaciones de Big Data.

---

## 1. Explicación y detalles de los datos

El dataset proviene de **FBref.com** (Sports Reference LLC), recopilado automáticamente cada semana mediante un pipeline ETL y publicado en Kaggle por Hubert Sidorowicz:

🔗 https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025

Cubre las **5 grandes ligas europeas** (Premier League, La Liga, Bundesliga, Serie A, Ligue 1) con estadísticas individuales acumuladas de la temporada 2024-2025. No es una muestra: incluye **todos los jugadores** que han disputado al menos un partido oficial. El uso es legítimo bajo licencia educativa y no comercial (Kaggle Open Dataset).

**Preguntas clave del proyecto:**
- ¿Qué variables tienen mayor correlación con la producción goleadora?
- ¿Existen diferencias significativas de rendimiento entre ligas?
- ¿Se puede predecir G+A a partir de métricas avanzadas (xG, xAG)?
- ¿Qué jugadores rinden por encima de lo esperado (*outperforming xG*)?

---

## 2. Selección e Integración de Datasets

El dataset principal contiene **28 variables** por jugador. Las más relevantes:

| Variable | Tipo | Descripción |
|----------|------|-------------|
| `Pos` | Categórica nominal | Posición (GK, DF, MF, FW) |
| `Comp` | Categórica nominal | Liga |
| `Gls`, `Ast`, `G+A` | Numérica discreta | Producción ofensiva |
| `xG`, `xAG` | Numérica continua | Expected Goals / Assisted Goals |
| `PrgC`, `PrgP`, `PrgR` | Numérica discreta | Acciones progresivas |
| `Gls/90`, `Ast/90` | Numérica continua | Rendimiento por 90 min |
| `market_value_eur_M` | Numérica continua | Valor de mercado (M€, Transfermarkt) |

El dataset se **enriquece** cruzando con datos de valor de mercado (Transfermarkt), usando `Player + Squad` como clave de unión.

**Análisis estadístico aplicado:**
- Estadística descriptiva (media, mediana, IQR, outliers)
- Correlación de Pearson (xG vs Gls, xAG vs Ast)
- ANOVA (Gls/90 por liga)
- Regresión lineal múltiple
- Clustering K-Means
- Árbol de decisión (clasificación)

---

## 3. Metodología CRISP-DM

Se aplica el modelo **CRISP-DM** por su naturaleza iterativa, adecuada para un dominio con alto ruido estadístico como el fútbol.

```
Comprensión     →  Comprensión   →  Preparación  →  Modelado
del negocio        de los datos      de datos
     ↑                                                   ↓
  Despliegue   ←  Evaluación  ←────────────────────────────
```

**Criterios de éxito:** R² > 0,75 en regresión (objetivo ambicioso con datos reales) · Silhouette Score > 0,25 en clustering · Accuracy > 70% en clasificación.

Consulta la [documentación completa de CRISP-DM](docs/) en la carpeta `docs/`.

---

## 4. Herramientas y Tecnologías

### 🐍 Python (Pandas · Matplotlib · Seaborn · Scikit-learn)

**¿Qué es?** Python es el lenguaje de referencia en Data Science. Las librerías utilizadas cubren el ciclo completo de análisis:

- **Pandas**: manipulación y limpieza de datos en DataFrames (estructura tabular en memoria).
- **Matplotlib / Seaborn**: generación de gráficas estadísticas (boxplots, scatterplots, heatmaps).
- **Scikit-learn**: implementación de modelos de machine learning con API unificada (`fit` / `predict` / `score`).

**Uso en el proyecto:** EDA completo, limpieza de datos, regresión lineal múltiple, Random Forest, K-Means, árbol de decisión y validación cruzada k-fold.

📄 Código: [`notebooks/01_eda_and_modeling.py`](notebooks/01_eda_and_modeling.py)

---

### 📊 R (Tidyverse — dplyr · ggplot2)

**¿Qué es?** R es el lenguaje estadístico por excelencia en investigación científica y análisis de datos. El metapaquete **Tidyverse** agrupa las librerías más utilizadas:

- **dplyr**: manipulación declarativa de datos (filter, group_by, summarise, mutate) con una sintaxis de pipeline `|>` muy legible.
- **ggplot2**: sistema de visualización basado en la *Grammar of Graphics*; produce gráficas publicación con pocas líneas de código.
- **readr**: carga de CSV rápida con inferencia automática de tipos.
- **forcats**: manejo de variables categóricas (factores).

**Funcionamiento:** R carga el CSV en un tibble (versión moderna del data.frame), aplica transformaciones con verbos dplyr y genera figuras guardadas como PNG con `ggsave()`.

**Uso en el proyecto:** Estadística descriptiva por liga (media, mediana, sd, IQR), ANOVA de Gls/90 entre ligas con post-hoc Tukey, análisis de correlación de Pearson, gráficas de violín por posición y ranking de outperformers.

📄 Código: [`r/football_analysis.R`](r/football_analysis.R)

---

### 🗄️ SQL (DuckDB / BigQuery)

**¿Qué es?** SQL (*Structured Query Language*) es el estándar para consultar bases de datos relacionales. **DuckDB** es un motor SQL embebido, analítico y de alto rendimiento que no requiere servidor; ideal para análisis local de archivos CSV y Parquet. **BigQuery** es su equivalente en la nube (Google Cloud), capaz de procesar petabytes.

**Funcionamiento:** Las consultas se ejecutan sobre tablas (en este caso, el CSV cargado directamente), permitiendo agregaciones, joins, filtros y funciones de ventana con sintaxis estándar ANSI SQL.

**Uso en el proyecto:** Consultas de exploración, ranking de jugadores, KPIs por liga, análisis de outliers y segmentación por valor de mercado.

📄 Código: [`sql/football_analysis.sql`](sql/football_analysis.sql)

---

### 🍊 Orange Data Mining

**¿Qué es?** Orange es una plataforma open-source de minería de datos y machine learning con interfaz visual de arrastrar y soltar, desarrollada por la Universidad de Liubliana. Permite construir flujos de trabajo (*workflows*) sin código, combinando nodos de carga de datos, preprocesamiento, modelos y evaluación.

**Funcionamiento:** Cada nodo del flujo representa una operación (cargar CSV, filtrar, entrenar un modelo, visualizar resultados). Los nodos se conectan mediante canales de datos y los resultados son interactivos en tiempo real.

**Uso en el proyecto:** Flujo visual que replica el pipeline de Python: carga del CSV → distribuciones → scatter xG/Goles → K-Means con Silhouette Plot → árbol de decisión → evaluación con validación cruzada k=5 y curva ROC, comparando simultáneamente Árbol, Regresión Logística y Random Forest.

📄 Workflow: [`orange/football_workflow.ows`](orange/football_workflow.ows)

---

### 🐘 Hadoop (HDFS)

**¿Qué es?** Hadoop es el framework de Big Data distribuido de Apache. Su componente **HDFS** (*Hadoop Distributed File System*) almacena datos a escala de petabytes dividiéndolos en bloques y replicándolos entre nodos para garantizar tolerancia a fallos.

**Funcionamiento:** El clúster se compone de un **NameNode** (índice del sistema de ficheros) y varios **DataNodes** (almacenamiento real). En este proyecto se despliega un clúster local de 3 nodos (1 NameNode + 2 DataNodes) mediante Docker.

**Uso en el proyecto:** Almacenamiento distribuido del dataset crudo y de los CSV procesados. Los datos se organizan en `/user/football/raw/`, `/user/football/processed/` y `/user/football/output/` en HDFS, con factor de replicación 2 (cada bloque existe en 2 DataNodes).

📄 Docker: [`hadoop/docker-compose.yml`](hadoop/docker-compose.yml)  
📄 Comandos HDFS: [`hadoop/hdfs_commands.sh`](hadoop/hdfs_commands.sh)

---

### 🌊 Apache NiFi

**¿Qué es?** Apache NiFi es una plataforma ETL (*Extract, Transform, Load*) con interfaz web visual. Permite diseñar pipelines de datos mediante procesadores gráficos, gestionar flujos en tiempo real y monitorizar cada paso con trazabilidad completa.

**Funcionamiento:** Un **FlowFile** (unidad de dato en NiFi) fluye de procesador en procesador: lectura → transformación → validación → destino. Cada procesador tiene configuración propia, políticas de reintentos y manejo de errores. Los flujos se exportan como plantillas XML reutilizables.

**Uso en el proyecto:** Pipeline ETL que lee el CSV desde disco local, añade metadatos (fuente, temporada, timestamp de ingesta), valida el esquema de columnas, filtra porteros y jugadores con menos de 90 minutos, y carga el resultado en HDFS.

📄 Template: [`nifi/football_etl_template.xml`](nifi/football_etl_template.xml)

---

### 📈 Tableau

**¿Qué es?** Tableau es la plataforma de visualización analítica de referencia en entornos empresariales. A diferencia de Power BI (orientado a informes), Tableau destaca en la exploración visual interactiva con acciones entre hojas, cálculos LOD (*Level of Detail*) y filtros en cascada.

**Funcionamiento:** Conecta a la fuente de datos (CSV, base de datos, etc.), infiere tipos automáticamente, y permite construir hojas de análisis que se combinan en un dashboard. Las acciones entre hojas permiten filtrar el dashboard al hacer clic en cualquier elemento.

**Uso en el proyecto:** Dashboard de 4 hojas equivalente al de Power BI: KPIs por liga, scatter xG vs Goles, ranking de jugadores y visualización de clusters K-Means, con filtros cruzados entre hojas.

📄 Guía paso a paso: [`tableau/football_tableau_guide.md`](tableau/football_tableau_guide.md)

---

### 📊 Power BI

**¿Qué es?** Herramienta de Business Intelligence de Microsoft para la creación de dashboards interactivos. Permite conectar múltiples fuentes de datos, aplicar transformaciones con Power Query y construir visualizaciones dinámicas con filtros, segmentadores y KPIs en tiempo real.

**Funcionamiento:** Importa el CSV enriquecido (`football_stats_enriched.csv`), crea relaciones entre tablas si las hay, y permite al usuario explorar los datos sin necesidad de código mediante arrastrar y soltar.

**Uso en el proyecto:** Dashboard con KPIs por liga (goles, xG, valor de mercado), scatter interactivo de jugadores, tabla de top performers y filtros por posición y equipo.

📄 Archivo: [`powerbi/football_dashboard.pbix`](powerbi/football_dashboard.pbix)

---

### 🗃️ Apache Cassandra

**¿Qué es?** Apache Cassandra es una base de datos NoSQL distribuida orientada a columnas. Diseñada para alta disponibilidad y escalabilidad horizontal sin punto único de fallo. Utiliza un modelo de datos basado en tablas con *partition keys* y *clustering keys* que determinan cómo se distribuyen y ordenan los datos entre nodos.

**Funcionamiento:** Los datos se organizan en *keyspaces* (equivalente a base de datos) que contienen tablas. La consulta CQL (*Cassandra Query Language*) es similar a SQL pero adaptada al modelo distribuido: las consultas deben incluir siempre la *partition key* para garantizar eficiencia. El factor de replicación controla en cuántos nodos se duplica cada partición.

**Uso en el proyecto:** Almacenamiento del dataset completo (958 jugadores) y del resumen por liga en Cassandra, usando `comp` (liga) como *partition key* para consultas eficientes por liga. El script Python carga ambos CSV usando el driver `cassandra-driver`.

📄 Schema CQL: [`cassandra/football_schema.cql`](cassandra/football_schema.cql)  
📄 Script carga: [`cassandra/cassandra_load.py`](cassandra/cassandra_load.py)

---

## 5. Implementación Práctica

### 5.1 Flujo del pipeline

```
[Kaggle CSV]  ──►  generate_sample_data.py  ──►  football_stats_2024_25.csv
                                                           │
                        ┌──────────────────────────────────┼──────────────────┐
                        ▼                                  ▼                  ▼
              Apache NiFi ETL                  01_eda_and_modeling.py    R (Tidyverse)
              (validar + limpiar)              ├── EDA + limpieza        ├── ANOVA ligas
              └── PutHDFS →                   ├── Regresión lineal / RF  ├── Correlaciones
                  HDFS /raw                   ├── K-Means Clustering     └── Visualizaciones
                                              ├── Árbol de decisión             ▼
                                              └── football_stats_enriched.csv  docs/figures/
                                                           │
                        ┌──────────────────────────────────┼──────────────────┐
                        ▼                                  ▼                  ▼
              SQL (DuckDB/BigQuery)            Power BI Dashboard         Tableau Dashboard
              (KPIs, rankings, outliers)       (4 páginas interactivas)   (4 hojas analíticas)
                        │
                        ▼
              Orange Data Mining
              (workflow visual ML)
                        │
                        ▼
              Apache Cassandra
              (almacenamiento NoSQL)
```

### 5.2 Resultados de los modelos

#### Regresión Lineal Múltiple (predecir G+A)

| Métrica | Valor |
|---------|-------|
| R² CV (5-fold) | 0,345 ± 0,064 |
| RMSE CV | 4,52 ± 0,19 |
| MAE | 3,56 |

Variables más influyentes: `xG` (coef. +0,28), `PrgC` (coef. +0,05), `xAG` (coef. +0,15).

#### Random Forest (comparativa)

| Métrica | Valor |
|---------|-------|
| R² CV (5-fold) | **0,452 ± 0,088** |

El Random Forest mejora la regresión lineal al capturar relaciones no lineales entre xG, minutos jugados y producción real.

#### K-Means Clustering (k=3)

| Cluster | Perfil | Gls medio | Ast medio | xG medio |
|---------|--------|-----------|-----------|----------|
| 0 | Delantero Goleador | 9,12 | 5,41 | 7,93 |
| 1 | Mediocampista Creativo | 3,83 | 6,17 | 4,08 |
| 2 | Defensor | 1,58 | 2,08 | 1,67 |

Silhouette Score: **0,312** — clusters bien diferenciados.

#### Árbol de Decisión (¿supera el jugador su xG?)

| Métrica | Valor |
|---------|-------|
| Accuracy CV | **74,5%** |
| F1-Score (clase positiva) | 0,80 |

La variable más discriminante es `xG ≤ 3,42`: jugadores con poca expectativa son más propensos a superarla.

### 5.3 Hallazgos principales

- **La Liga** tiene la mayor producción ofensiva media (9,93 G+A/jugador) y el mayor porcentaje de jugadores que superan su xG (58,8%).
- El **55,7% de los jugadores de campo** supera sus expected goals, lo que indica que el xG es un predictor conservador en la práctica.
- Existe una **correlación fuerte** entre `xG` y `Gls` (r ≈ 0,82 en FW), pero con alta varianza individual.
- El **valor de mercado** se correlaciona más con la producción acumulada que con el rendimiento por 90 minutos.

---

## 6. Resultados y Visualizaciones

> Las figuras generadas se encuentran en [`docs/figures/`](docs/figures/)

**Figuras generadas con Python** ([`docs/figures/`](docs/figures/)):

| Figura | Descripción |
|--------|-------------|
| `01_distribucion_goles_posicion.png` | Boxplot G/A/G+A por posición |
| `02_goles90_por_liga.png` | Gls/90 por liga (base ANOVA) |
| `03_heatmap_correlaciones.png` | Matriz de correlación |
| `04_scatter_xg_vs_goles.png` | xG vs Goles reales por posición |
| `05_valor_mercado_vs_ga.png` | Valor de mercado vs G+A |
| `06_top15_jugadores_ga.png` | Top 15 jugadores por G+A |
| `07_regresion_residuos.png` | Residuos y Real vs Predicho |
| `08_feature_importance_rf.png` | Importancia de variables (RF) |
| `09_kmeans_elbow_silhouette.png` | Elbow + Silhouette (K-Means) |
| `10_kmeans_clusters_scatter.png` | Clusters de jugadores (scatter) |
| `11_confusion_matrix_dt.png` | Matriz de confusión árbol de decisión |

**Figuras generadas con R** ([`docs/figures/`](docs/figures/)):

| Figura | Descripción |
|--------|-------------|
| `R_01_heatmap_correlaciones.png` | Heatmap correlaciones (corrplot) |
| `R_02_anova_goles90_liga.png` | ANOVA Gls/90 por liga (boxplot ggplot2) |
| `R_03_scatter_xg_goles.png` | Scatter xG vs Goles por posición (con regresión) |
| `R_04_top15_GA.png` | Top 15 G+A (barras horizontales ggplot2) |
| `R_05_violin_GA_posicion.png` | Violín G+A por posición con jitter |
| `R_06_outperformers_xG.png` | Top jugadores que superan su xG |

---

## 📌 Conclusiones

1. Las métricas avanzadas (xG, xAG) tienen un poder predictivo real pero limitado: el Random Forest con R²=0,45 muestra que el rendimiento ofensivo depende también de factores no capturados (compañeros, sistema táctico, forma física).
2. El clustering identifica perfiles de jugadores coherentes con el conocimiento del dominio, lo que valida la calidad del dataset.
3. La Liga destaca como la liga con mayor producción ofensiva, pero Ligue 1 tiene los jugadores con mayor xG individual.
4. Para futuros trabajos, se recomienda incorporar datos de partidos individuales (no solo acumulados) y métricas defensivas para construir un índice de rendimiento global.

---

## 📚 Bibliografía

- FBref.com — Sports Reference LLC. *Football Statistics and History*. https://fbref.com
- Sidorowicz, H. (2024). *Football Players Stats 2024-2025*. Kaggle. https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025
- Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc.
- Pedregosa, F. et al. (2011). *Scikit-learn: Machine Learning in Python*. JMLR 12, 2825-2830.
- McKinney, W. (2010). *Data Structures for Statistical Computing in Python*. Proceedings of the 9th Python in Science Conference.
- Wickham, H. et al. (2019). *Welcome to the Tidyverse*. Journal of Open Source Software, 4(43), 1686.
- Wickham, H. (2016). *ggplot2: Elegant Graphics for Data Analysis*. Springer-Verlag New York.
- Demšar, J. et al. (2013). *Orange: Data Mining Toolbox in Python*. JMLR 14, 2349-2353.
- White, T. (2015). *Hadoop: The Definitive Guide* (4ª ed.). O'Reilly Media.
- Apache Software Foundation. (2024). *Apache NiFi Documentation*. https://nifi.apache.org/docs.html
- Hewitt, E. (2010). *Cassandra: The Definitive Guide*. O'Reilly Media.
- Microsoft. (2024). *Power BI Documentation*. https://docs.microsoft.com/power-bi
- Tableau Software. (2024). *Tableau Desktop and Web Authoring Help*. https://help.tableau.com
- Anthropic Claude AI — apoyo en redacción y estructuración del proyecto.

---

## 📁 Estructura del repositorio

```
football-bigdata-project/
│
├── README.md                          # Este archivo
│
├── data/
│   ├── generate_sample_data.py        # Generador de datos de muestra
│   ├── football_stats_2024_25.csv     # Dataset principal (o descargar de Kaggle)
│   └── football_stats_enriched.csv    # Dataset enriquecido con predicciones y clusters
│
├── notebooks/
│   └── 01_eda_and_modeling.py         # Pipeline completo: EDA + ML
│
├── sql/
│   └── football_analysis.sql          # Consultas SQL analíticas
│
├── powerbi/
│   └── football_dashboard.pbix        # Dashboard Power BI
│
├── orange/
│   └── football_workflow.ows          # Flujo Orange Data Mining (opcional)
│
└── docs/
    ├── informe_final.pdf              # Informe final del proyecto
    └── figures/                       # Gráficas generadas por Python
        ├── 01_distribucion_goles_posicion.png
        ├── 02_goles90_por_liga.png
        ├── 03_heatmap_correlaciones.png
        ├── 04_scatter_xg_vs_goles.png
        ├── 05_valor_mercado_vs_ga.png
        ├── 06_top15_jugadores_ga.png
        ├── 07_regresion_residuos.png
        ├── 08_feature_importance_rf.png
        ├── 09_kmeans_elbow_silhouette.png
        ├── 10_kmeans_clusters_scatter.png
        └── 11_confusion_matrix_dt.png
```

---

*Proyecto académico — Especialidad Big Data e IA · España · 2024-2025*
