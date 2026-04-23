#!/usr/bin/env bash
# ============================================================
# Comandos HDFS — Football Stats 2024-2025
# Proyecto Final Big Data e IA — España 2024-2025
# ============================================================
# Pre-requisito: clúster arriba con docker-compose up -d
#   Acceder al namenode:
#   docker exec -it hadoop-namenode bash
# ============================================================

# ── 1. VERIFICAR ESTADO DEL CLÚSTER ────────────────────────
echo "=== Estado del clúster HDFS ==="
hdfs dfsadmin -report

# ── 2. CREAR ESTRUCTURA DE DIRECTORIOS EN HDFS ─────────────
echo "=== Creando directorios en HDFS ==="
hdfs dfs -mkdir -p /user/football/raw
hdfs dfs -mkdir -p /user/football/processed
hdfs dfs -mkdir -p /user/football/output

hdfs dfs -ls /user/football/

# ── 3. SUBIR EL DATASET AL CLÚSTER ─────────────────────────
echo "=== Subiendo dataset a HDFS ==="

# Copiar desde la carpeta local montada en el contenedor
hdfs dfs -put /data_upload/football_stats_2024_25.csv \
              /user/football/raw/football_stats_2024_25.csv

hdfs dfs -put /data_upload/football_stats_enriched.csv \
              /user/football/processed/football_stats_enriched.csv

hdfs dfs -put /data_upload/summary_by_league.csv \
              /user/football/output/summary_by_league.csv

# ── 4. VERIFICAR ARCHIVOS SUBIDOS ───────────────────────────
echo "=== Archivos en HDFS ==="
hdfs dfs -ls -h /user/football/raw/
hdfs dfs -ls -h /user/football/processed/
hdfs dfs -ls -h /user/football/output/

# ── 5. INSPECCIONAR EL DATASET (primeras líneas) ────────────
echo "=== Primeras 5 filas del dataset raw ==="
hdfs dfs -cat /user/football/raw/football_stats_2024_25.csv | head -5

# ── 6. CONTAR REGISTROS ─────────────────────────────────────
echo "=== Número de líneas en el dataset ==="
hdfs dfs -cat /user/football/raw/football_stats_2024_25.csv | wc -l

# ── 7. VERIFICAR REPLICACIÓN (factor=2, 2 DataNodes) ────────
echo "=== Información del bloque y replicación ==="
hdfs fsck /user/football/raw/football_stats_2024_25.csv \
     -files -blocks -locations

# ── 8. ESPACIO EN DISCO ─────────────────────────────────────
echo "=== Uso de espacio en HDFS ==="
hdfs dfs -du -s -h /user/football/

# ── 9. DESCARGAR UN ARCHIVO DEL HDFS (si se necesita) ───────
# hdfs dfs -get /user/football/output/summary_by_league.csv /tmp/

# ── 10. ELIMINAR ARCHIVOS (limpieza) ────────────────────────
# hdfs dfs -rm -r /user/football/raw/
