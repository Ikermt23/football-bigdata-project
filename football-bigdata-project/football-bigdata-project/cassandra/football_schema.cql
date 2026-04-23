-- ============================================================
-- Apache Cassandra — Schema Football Stats 2024-2025
-- Proyecto Final Big Data e IA — España 2024-2025
-- ============================================================
-- Conexión local:  cqlsh localhost 9042
-- Con Docker:      docker exec -it cassandra-football cqlsh
-- ============================================================

-- ── 1. KEYSPACE ────────────────────────────────────────────

CREATE KEYSPACE IF NOT EXISTS football_stats
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE football_stats;

-- ── 2. TABLA PRINCIPAL: jugadores ──────────────────────────
-- Partition key: comp (liga) → permite consultas por liga eficientes
-- Clustering key: ga DESC → ordena por producción ofensiva descendente

CREATE TABLE IF NOT EXISTS players (
    comp            TEXT,
    player          TEXT,
    squad           TEXT,
    nation          TEXT,
    pos             TEXT,
    age             INT,
    mp              INT,
    starts          INT,
    min             INT,
    gls             FLOAT,
    ast             FLOAT,
    ga              FLOAT,
    g_pk            FLOAT,
    pk              INT,
    pkatt           INT,
    crdy            INT,
    crdr            INT,
    xg              FLOAT,
    npxg            FLOAT,
    xag             FLOAT,
    npxg_xag        FLOAT,
    prgc            INT,
    prgp            INT,
    prgr            INT,
    gls_90          FLOAT,
    ast_90          FLOAT,
    xg_90           FLOAT,
    market_value_eur_m FLOAT,
    -- columnas enriquecidas (del CSV procesado por Python)
    over_xg         INT,
    cluster         INT,
    cluster_label   TEXT,
    ga_pred_lr      FLOAT,
    ga_pred_rf      FLOAT,
    xg_diff         FLOAT,
    PRIMARY KEY ((comp), ga, player)
) WITH CLUSTERING ORDER BY (ga DESC, player ASC)
  AND comment = 'Estadísticas de jugadores de fútbol — 5 grandes ligas 2024-2025'
  AND gc_grace_seconds = 86400;

-- ── 3. TABLA AUXILIAR: resumen por liga ────────────────────

CREATE TABLE IF NOT EXISTS summary_by_league (
    comp                TEXT PRIMARY KEY,
    n_jugadores         INT,
    media_ga            FLOAT,
    media_xg            FLOAT,
    pct_over_xg         FLOAT,
    media_valor_m       FLOAT
) WITH comment = 'KPIs agregados por liga';

-- ── 4. ÍNDICE SECUNDARIO: búsqueda por posición ────────────

CREATE INDEX IF NOT EXISTS idx_pos ON players (pos);
CREATE INDEX IF NOT EXISTS idx_cluster ON players (cluster);

-- ── 5. CONSULTAS DE EJEMPLO ────────────────────────────────

-- Top 10 jugadores de La Liga por G+A
SELECT player, squad, pos, gls, ast, ga, xg, xg_diff
FROM players
WHERE comp = 'La Liga'
LIMIT 10;

-- Top 10 de Premier League
SELECT player, squad, pos, gls, ast, ga, xg, xg_diff
FROM players
WHERE comp = 'Premier League'
LIMIT 10;

-- Jugadores de campo en un cluster concreto (requiere índice)
SELECT player, squad, comp, pos, ga, cluster_label
FROM players
WHERE cluster = 0
ALLOW FILTERING;

-- Resumen de todas las ligas
SELECT * FROM summary_by_league;

-- ── 6. LIMPIEZA (ejecutar solo si se quiere reiniciar) ──────
-- DROP TABLE IF EXISTS players;
-- DROP TABLE IF EXISTS summary_by_league;
-- DROP KEYSPACE IF EXISTS football_stats;
