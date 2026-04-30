# Tableau — Dashboard Football Stats 2024-2025

## Requisitos

- **Tableau Desktop** (prueba gratuita 14 días) o **Tableau Public** (gratuito, guarda en la nube)
- Archivo de datos: `data/football_stats_enriched.csv`

## Pasos para reproducir el dashboard

### 1. Conectar a los datos

1. Abrir Tableau Desktop / Public
2. En el panel izquierdo: **Conectar → Archivo de texto**
3. Seleccionar `data/football_stats_enriched.csv`
4. En la vista de origen de datos, verificar tipos:
   - `Comp`, `Pos`, `Squad`, `Player`, `cluster_label` → Dimensión (cadena)
   - `Gls`, `Ast`, `G+A`, `xG`, `xG_diff`, `Min`, `market_value_eur_M` → Medida (número)
5. Hacer clic en **Hoja 1** para comenzar

### 2. Campos calculados (equivalentes a DAX de Power BI)

Crear desde **Análisis → Crear campo calculado**:

| Nombre | Fórmula |
|--------|---------|
| `xG_diff` | `[Gls] - [xG]` |
| `Rendimiento_relativo` | `([G+A] / [Min]) * 90` |
| `Over_xG_label` | `IF [over_xg] = 1 THEN "Supera xG" ELSE "No supera xG" END` |

### 3. Hoja 1 — KPIs por Liga

1. Arrastrar `Comp` a **Columnas**
2. Arrastrar `G+A` (medida) a **Filas** → cambiar a **Promedio**
3. Tipo de gráfico: **Barras**
4. Arrastrar `Comp` a **Color** (paleta Set2)
5. Arrastrar `Pos` a **Filtros** → mostrar filtro como lista desplegable
6. Título: *"Media de G+A por Liga — Temporada 2024-2025"*

### 4. Hoja 2 — Scatter xG vs Goles

1. Arrastrar `xG` a **Columnas**, `Gls` a **Filas**
2. Tipo de gráfico: **Dispersión** (automático)
3. Arrastrar `Pos` a **Color**
4. Arrastrar `Player` a **Detalle**
5. Arrastrar `Min` a **Tamaño** (puntos proporcionales a minutos)
6. Agregar **línea de referencia**: Análisis → Línea de referencia → constante y=x
7. Arrastrar `Comp` a **Filtros** → mostrar como selector
8. Título: *"Expected Goals vs Goles reales por posición"*

### 5. Hoja 3 — Tabla Top Jugadores

1. Arrastrar `Player`, `Squad`, `Comp`, `Pos` a **Filas**
2. Arrastrar `Gls`, `Ast`, `G+A`, `xG_diff`, `market_value_eur_M` a **Medidas de texto**
3. Ordenar por `G+A` descendente
4. Agregar segmentadores: `Comp`, `Pos`
5. Título: *"Ranking de jugadores por G+A"*

### 6. Hoja 4 — Perfiles de Jugadores (Clustering)

1. Arrastrar `xG` a **Columnas**, `G+A` a **Filas**
2. Arrastrar `cluster_label` a **Color**
3. Arrastrar `Player` a **Detalle** (tooltip al pasar el ratón)
4. Título: *"Perfiles de jugadores — K-Means (k=3)"*

### 7. Crear el Dashboard

1. Nueva hoja: **Dashboard → Nuevo Dashboard**
2. Tamaño: **Automático** (adapta a pantalla)
3. Arrastrar las 4 hojas al lienzo
4. Activar **"Usar como filtro"** en la hoja de KPIs por Liga
   (al hacer clic en una liga, las demás hojas se filtran automáticamente)
5. Añadir texto: título del proyecto, fuente de datos, fecha
6. Guardar: `tableau/football_dashboard.twbx`
   - `.twbx` incluye los datos empaquetados (portable)
   - `.twb` solo el layout (requiere CSV externo)

## Diferencias con Power BI

| Característica | Power BI | Tableau |
|---|---|---|
| Lenguaje de fórmulas | DAX | LOD Expressions |
| Filtros cruzados | Automáticos | Requieren "Usar como filtro" |
| Publicación gratuita | Power BI Service (limitado) | Tableau Public |
| Mejor para | Informes corporativos | Exploración analítica |

## Capturas de referencia

Las capturas del dashboard deben guardarse en:
- `docs/figures/Tableau_01_kpis_liga.png`
- `docs/figures/Tableau_02_scatter_xg.png`
- `docs/figures/Tableau_03_top_jugadores.png`
- `docs/figures/Tableau_04_clusters.png`
