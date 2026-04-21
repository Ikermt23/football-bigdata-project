-- ============================================================
-- football_analysis.sql
-- Proyecto Final Big Data — Football Players Stats 2024-2025
-- Herramienta: SQL (compatible BigQuery y SQLite)
-- ============================================================
-- NOTA: En BigQuery, reemplaza `football_stats` por
--       `tu_proyecto.tu_dataset.football_stats`
-- ============================================================


-- ── 1. EXPLORACIÓN INICIAL ───────────────────────────────────────────────────

-- Total de jugadores y ligas disponibles
SELECT
    COUNT(*)          AS total_jugadores,
    COUNT(DISTINCT Comp)  AS total_ligas,
    COUNT(DISTINCT Squad) AS total_equipos,
    COUNT(DISTINCT Pos)   AS posiciones
FROM football_stats;


-- Distribución de jugadores por posición y liga
SELECT
    Comp,
    Pos,
    COUNT(*) AS jugadores,
    ROUND(AVG(Gls), 2)  AS media_goles,
    ROUND(AVG(Ast), 2)  AS media_asistencias,
    ROUND(AVG(xG),  2)  AS media_xG
FROM football_stats
WHERE Pos != 'GK'
  AND Min  >= 90
GROUP BY Comp, Pos
ORDER BY Comp, Pos;


-- ── 2. RANKING DE JUGADORES ──────────────────────────────────────────────────

-- Top 20 jugadores por producción ofensiva (G+A)
SELECT
    Player,
    Pos,
    Squad,
    Comp,
    Gls,
    Ast,
    "G+A"                           AS ga_total,
    xG,
    ROUND("G+A" - (xG + xAG), 2)   AS over_performance,
    market_value_eur_M
FROM football_stats
WHERE Pos != 'GK'
  AND Min  >= 450
ORDER BY "G+A" DESC
LIMIT 20;


-- Jugadores que más superan su xG (outperformers)
SELECT
    Player,
    Squad,
    Comp,
    Pos,
    Gls,
    xG,
    ROUND(Gls - xG, 2)  AS xG_diff,
    "G+A",
    market_value_eur_M
FROM football_stats
WHERE Pos  != 'GK'
  AND Min  >= 450
  AND Gls   > xG
ORDER BY xG_diff DESC
LIMIT 15;


-- Jugadores que rinden por DEBAJO de su xG (underperformers)
SELECT
    Player,
    Squad,
    Comp,
    Pos,
    Gls,
    xG,
    ROUND(Gls - xG, 2)  AS xG_diff,
    "G+A"
FROM football_stats
WHERE Pos  != 'GK'
  AND Min  >= 450
  AND Gls   < xG
ORDER BY xG_diff ASC
LIMIT 15;


-- ── 3. ANÁLISIS POR LIGA (BASE PARA ANOVA) ──────────────────────────────────

-- KPIs de rendimiento por liga
SELECT
    Comp                                AS liga,
    COUNT(*)                            AS jugadores,
    ROUND(AVG(Gls),    2)               AS media_goles,
    ROUND(AVG(Ast),    2)               AS media_asistencias,
    ROUND(AVG("G+A"),  2)               AS media_ga,
    ROUND(AVG(xG),     2)               AS media_xG,
    ROUND(AVG(xAG),    2)               AS media_xAG,
    ROUND(AVG("Gls/90"), 3)             AS media_gls_90,
    ROUND(AVG(market_value_eur_M), 1)   AS valor_medio_M,
    ROUND(
        100.0 * SUM(CASE WHEN Gls > xG THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                   AS pct_over_xG
FROM football_stats
WHERE Pos != 'GK'
  AND Min  >= 90
GROUP BY Comp
ORDER BY media_ga DESC;


-- ── 4. ANÁLISIS POR EQUIPO ───────────────────────────────────────────────────

-- Equipos más goleadores (suma total de G+A)
SELECT
    Squad,
    Comp,
    COUNT(*)            AS jugadores,
    SUM(Gls)            AS goles_totales,
    SUM(Ast)            AS asistencias_totales,
    SUM("G+A")          AS ga_totales,
    ROUND(AVG(xG), 2)   AS xG_medio,
    ROUND(AVG(market_value_eur_M), 1) AS valor_plantilla_medio_M
FROM football_stats
WHERE Pos != 'GK'
GROUP BY Squad, Comp
ORDER BY ga_totales DESC
LIMIT 15;


-- ── 5. ANÁLISIS DE EDAD ──────────────────────────────────────────────────────

-- Rendimiento por tramo de edad
SELECT
    CASE
        WHEN Age < 21 THEN 'Sub-21'
        WHEN Age < 25 THEN '21-24'
        WHEN Age < 29 THEN '25-28'
        WHEN Age < 33 THEN '29-32'
        ELSE               '33+'
    END                             AS tramo_edad,
    COUNT(*)                        AS jugadores,
    ROUND(AVG(Gls),    2)           AS media_goles,
    ROUND(AVG("Gls/90"), 3)         AS media_gls_90,
    ROUND(AVG(xG),     2)           AS media_xG,
    ROUND(AVG(market_value_eur_M),1) AS valor_medio_M
FROM football_stats
WHERE Pos != 'GK'
  AND Min  >= 90
GROUP BY tramo_edad
ORDER BY tramo_edad;


-- ── 6. CORRELACIÓN VALOR DE MERCADO ─────────────────────────────────────────

-- ¿El rendimiento justifica el valor de mercado?
-- Segmentación por cuartiles de valor de mercado
SELECT
    CASE
        WHEN market_value_eur_M < 25  THEN '< 25M'
        WHEN market_value_eur_M < 75  THEN '25-75M'
        WHEN market_value_eur_M < 125 THEN '75-125M'
        ELSE                               '> 125M'
    END                             AS rango_valor,
    COUNT(*)                        AS jugadores,
    ROUND(AVG(Gls),   2)            AS media_goles,
    ROUND(AVG(Ast),   2)            AS media_asistencias,
    ROUND(AVG("G+A"), 2)            AS media_ga,
    ROUND(AVG(xG),    2)            AS media_xG,
    ROUND(AVG("Gls/90"), 3)         AS media_gls_90
FROM football_stats
WHERE Pos != 'GK'
  AND Min  >= 90
GROUP BY rango_valor
ORDER BY media_ga DESC;


-- ── 7. DETECCIÓN DE OUTLIERS ─────────────────────────────────────────────────

-- Jugadores estadísticamente atípicos: alto xG pero pocos goles reales
SELECT
    Player,
    Pos,
    Squad,
    Comp,
    Gls,
    xG,
    ROUND(xG - Gls, 2)  AS xG_no_convertido,
    Min
FROM football_stats
WHERE Pos   != 'GK'
  AND Min   >= 450
  AND xG     > 8
  AND Gls    < xG * 0.5   -- convirtió menos del 50% de sus xG
ORDER BY xG_no_convertido DESC
LIMIT 10;
