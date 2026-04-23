"""
Football Stats 2024-2025 — Carga de datos en Apache Cassandra
Proyecto Final Big Data e IA — España 2024-2025

Requisitos:
    pip install cassandra-driver pandas

Arrancar Cassandra con Docker:
    docker run -d --name cassandra-football -p 9042:9042 cassandra:4.1

Ejecutar este script:
    python cassandra/cassandra_load.py
"""

import pandas as pd
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import BatchStatement, SimpleStatement
from datetime import datetime

# ── Configuración de conexión ────────────────────────────────
CASSANDRA_HOST = "127.0.0.1"
CASSANDRA_PORT = 9042
KEYSPACE       = "football_stats"

# Rutas de datos (relativas al directorio raíz del proyecto)
CSV_ENRICHED   = "data/football_stats_enriched.csv"
CSV_SUMMARY    = "data/summary_by_league.csv"


def conectar():
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT)
    session = cluster.connect()
    print(f"[OK] Conectado a Cassandra {CASSANDRA_HOST}:{CASSANDRA_PORT}")
    return cluster, session


def crear_schema(session):
    """Crea el keyspace y las tablas si no existen."""
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
    """)
    session.set_keyspace(KEYSPACE)

    session.execute("""
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
            over_xg         INT,
            cluster         INT,
            cluster_label   TEXT,
            ga_pred_lr      FLOAT,
            ga_pred_rf      FLOAT,
            xg_diff         FLOAT,
            PRIMARY KEY ((comp), ga, player)
        ) WITH CLUSTERING ORDER BY (ga DESC, player ASC)
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS summary_by_league (
            comp            TEXT PRIMARY KEY,
            n_jugadores     INT,
            media_ga        FLOAT,
            media_xg        FLOAT,
            pct_over_xg     FLOAT,
            media_valor_m   FLOAT
        )
    """)

    print("[OK] Keyspace y tablas creados/verificados")


def cargar_jugadores(session, csv_path: str):
    """Carga el CSV enriquecido en la tabla players."""
    df = pd.read_csv(csv_path)
    print(f"[INFO] Cargando {len(df)} jugadores desde {csv_path}...")

    insert_stmt = session.prepare("""
        INSERT INTO players (
            comp, player, squad, nation, pos, age, mp, starts, min,
            gls, ast, ga, g_pk, pk, pkatt, crdy, crdr,
            xg, npxg, xag, npxg_xag, prgc, prgp, prgr,
            gls_90, ast_90, xg_90, market_value_eur_m,
            over_xg, cluster, cluster_label, ga_pred_lr, ga_pred_rf, xg_diff
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?
        )
    """)

    col_map = {
        "G+A": "ga", "G-PK": "g_pk", "npxG+xAG": "npxg_xag",
        "Gls/90": "gls_90", "Ast/90": "ast_90", "xG/90": "xg_90",
        "market_value_eur_M": "market_value_eur_m",
        "GA_pred_lr": "ga_pred_lr", "GA_pred_rf": "ga_pred_rf",
    }
    df = df.rename(columns=col_map)
    df.columns = [c.lower() for c in df.columns]

    errores = 0
    for i, row in df.iterrows():
        try:
            session.execute(insert_stmt, (
                str(row.get("comp", "")),
                str(row.get("player", "")),
                str(row.get("squad", "")),
                str(row.get("nation", "")),
                str(row.get("pos", "")),
                int(row.get("age", 0)),
                int(row.get("mp", 0)),
                int(row.get("starts", 0)),
                int(row.get("min", 0)),
                float(row.get("gls", 0)),
                float(row.get("ast", 0)),
                float(row.get("ga", 0)),
                float(row.get("g_pk", 0)),
                int(row.get("pk", 0)),
                int(row.get("pkatt", 0)),
                int(row.get("crdy", 0)),
                int(row.get("crdr", 0)),
                float(row.get("xg", 0)),
                float(row.get("npxg", 0)),
                float(row.get("xag", 0)),
                float(row.get("npxg_xag", 0)),
                int(row.get("prgc", 0)),
                int(row.get("prgp", 0)),
                int(row.get("prgr", 0)),
                float(row.get("gls_90", 0)),
                float(row.get("ast_90", 0)),
                float(row.get("xg_90", 0)),
                float(row.get("market_value_eur_m", 0)),
                int(row.get("over_xg", 0)),
                int(row.get("cluster", -1)),
                str(row.get("cluster_label", "")),
                float(row.get("ga_pred_lr", 0)),
                float(row.get("ga_pred_rf", 0)),
                float(row.get("xg_diff", 0)),
            ))
        except Exception as e:
            errores += 1
            if errores <= 3:
                print(f"  [WARN] Fila {i}: {e}")

    print(f"[OK] {len(df) - errores} jugadores insertados ({errores} errores)")


def cargar_resumen(session, csv_path: str):
    """Carga el CSV de resumen por liga."""
    df = pd.read_csv(csv_path)
    print(f"[INFO] Cargando resumen de {len(df)} ligas...")

    for _, row in df.iterrows():
        session.execute("""
            INSERT INTO summary_by_league
            (comp, n_jugadores, media_ga, media_xg, pct_over_xg, media_valor_m)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            str(row.get("Comp", row.get("comp", ""))),
            int(row.get("n_jugadores", 0)),
            float(row.get("media_GA", row.get("media_ga", 0))),
            float(row.get("media_xG", row.get("media_xg", 0))),
            float(row.get("pct_over_xG", row.get("pct_over_xg", 0))),
            float(row.get("media_valor_M", row.get("media_valor_m", 0))),
        ))

    print(f"[OK] Resumen por liga insertado")


def verificar_datos(session):
    """Consultas de verificación tras la carga."""
    print("\n=== VERIFICACIÓN: Top 5 jugadores La Liga ===")
    rows = session.execute("""
        SELECT player, squad, pos, gls, ast, ga, xg_diff
        FROM players
        WHERE comp = 'La Liga'
        LIMIT 5
    """)
    for r in rows:
        print(f"  {r.player:25s} | {r.squad:20s} | {r.pos} | "
              f"G:{r.gls:.0f} A:{r.ast:.0f} GA:{r.ga:.0f} "
              f"xG_diff:{r.xg_diff:+.1f}")

    print("\n=== VERIFICACIÓN: Resumen por liga ===")
    rows = session.execute("SELECT * FROM summary_by_league")
    for r in rows:
        print(f"  {r.comp:20s} | {r.n_jugadores} jugadores | "
              f"G+A medio: {r.media_ga:.2f} | over_xG: {r.pct_over_xg:.1f}%")


def main():
    print(f"\n{'='*60}")
    print("  Football Stats 2024-2025 → Apache Cassandra")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    cluster, session = conectar()
    try:
        crear_schema(session)
        cargar_jugadores(session, CSV_ENRICHED)
        cargar_resumen(session, CSV_SUMMARY)
        verificar_datos(session)
        print("\n[COMPLETADO] Datos cargados correctamente en Cassandra")
    finally:
        cluster.shutdown()


if __name__ == "__main__":
    main()
