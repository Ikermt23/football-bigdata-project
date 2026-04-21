"""
01_eda_and_modeling.py
=====================
Proyecto Final Big Data — Football Players Stats 2024-2025
Punto 5: Implementación Práctica

Herramienta: Python (Pandas, Matplotlib, Seaborn, Scikit-learn)
Cubre:
  - EDA completo (distribuciones, correlaciones, outliers)
  - Limpieza y preparación de datos (CRISP-DM Fase 3)
  - Regresión lineal múltiple para predecir G+A
  - K-Means Clustering de perfiles de jugadores
  - Árbol de decisión: ¿rinde por encima de xG?
  - Exportación de resultados para Power BI

Autor: Proyecto Final Especialidad Big Data
Dataset: football_stats_2024_25.csv (generado desde FBref / Kaggle)
"""

# ── 0. IMPORTS ────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import (mean_squared_error, mean_absolute_error,
                              r2_score, classification_report,
                              confusion_matrix, silhouette_score)
import warnings, os

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

OUTPUT_DIR = "/home/claude/football-bigdata-project/docs/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save(fig, name):
    path = f"{OUTPUT_DIR}/{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] guardado → {path}")


# ── 1. CARGA DE DATOS ────────────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 2 — Comprensión de los datos")
print("="*60)

df = pd.read_csv("/home/claude/football-bigdata-project/data/football_stats_2024_25.csv")
print(f"\nRegistros cargados : {len(df)}")
print(f"Columnas           : {len(df.columns)}")
print(f"\nTipos de datos:\n{df.dtypes.to_string()}")
print(f"\nNulos por columna:\n{df.isnull().sum()[df.isnull().sum() > 0].to_string()}")
print(f"\nEstadística descriptiva (variables clave):")
print(df[["Age","Min","Gls","Ast","xG","xAG","G+A","market_value_eur_M"]].describe().round(2).to_string())


# ── 2. LIMPIEZA Y PREPARACIÓN ────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 3 — Preparación de los datos")
print("="*60)

# Separar porteros (su análisis es independiente)
df_gk  = df[df["Pos"] == "GK"].copy()
df_out = df[df["Pos"] != "GK"].copy()
print(f"\nPorteros separados : {len(df_gk)}")
print(f"Jugadores de campo : {len(df_out)}")

# Filtrar jugadores con < 90 minutos (sesgo en métricas /90)
df_out = df_out[df_out["Min"] >= 90].copy()
print(f"Tras filtrar <90 min: {len(df_out)} jugadores")

# Imputar nulos residuales con mediana
num_cols = df_out.select_dtypes(include=np.number).columns
df_out[num_cols] = df_out[num_cols].fillna(df_out[num_cols].median())

# Variable objetivo binaria: ¿rinde por encima de xG?
df_out["over_xG"] = (df_out["Gls"] > df_out["xG"]).astype(int)
print(f"\nJugadores que superan su xG: {df_out['over_xG'].sum()} "
      f"({df_out['over_xG'].mean()*100:.1f}%)")


# ── 3. EDA — VISUALIZACIONES ─────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 2 — Análisis Exploratorio (EDA)")
print("="*60)

# 3.1 Distribución de goles por posición
print("\n[1/6] Distribución de goles por posición...")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Distribución de Variables Ofensivas por Posición", fontsize=14, fontweight="bold")
for ax, col, title in zip(axes, ["Gls", "Ast", "G+A"],
                          ["Goles", "Asistencias", "Goles + Asistencias"]):
    sns.boxplot(data=df_out, x="Pos", y=col, ax=ax, palette="Set2")
    ax.set_title(title)
    ax.set_xlabel("Posición")
    ax.set_ylabel(col)
save(fig, "01_distribucion_goles_posicion")

# 3.2 Goles por liga (ANOVA visual)
print("[2/6] Comparativa por liga...")
fig, ax = plt.subplots(figsize=(12, 5))
sns.boxplot(data=df_out, x="Comp", y="Gls/90", palette="coolwarm", ax=ax)
ax.set_title("Goles/90 min por Liga (base para ANOVA)", fontsize=13, fontweight="bold")
ax.set_xlabel("Liga")
ax.set_ylabel("Goles por 90 minutos")
plt.xticks(rotation=15)
save(fig, "02_goles90_por_liga")

# 3.3 Heatmap de correlaciones
print("[3/6] Mapa de correlaciones...")
corr_cols = ["Gls","Ast","G+A","xG","xAG","npxG","npxG+xAG",
             "Min","PrgC","PrgP","PrgR","CrdY","market_value_eur_M"]
corr = df_out[corr_cols].corr()
fig, ax = plt.subplots(figsize=(12, 9))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, linewidths=0.5, ax=ax, annot_kws={"size": 8})
ax.set_title("Matriz de Correlación — Variables Numéricas", fontsize=13, fontweight="bold")
save(fig, "03_heatmap_correlaciones")

# 3.4 xG vs Goles reales (scatter por posición)
print("[4/6] Scatter xG vs Goles reales...")
fig, ax = plt.subplots(figsize=(9, 7))
colors = {"DF": "#3498db", "MF": "#2ecc71", "FW": "#e74c3c"}
for pos, grp in df_out.groupby("Pos"):
    ax.scatter(grp["xG"], grp["Gls"], alpha=0.5, s=30,
               label=pos, color=colors.get(pos, "gray"))
lims = [0, df_out[["xG","Gls"]].max().max() + 2]
ax.plot(lims, lims, "k--", linewidth=1, label="xG = Goles (referencia)")
ax.set_xlim(lims); ax.set_ylim(lims)
ax.set_xlabel("Expected Goals (xG)"); ax.set_ylabel("Goles reales")
ax.set_title("Goles Reales vs xG — Calibración del Modelo Predictivo",
             fontsize=12, fontweight="bold")
ax.legend()
save(fig, "04_scatter_xg_vs_goles")

# 3.5 Rendimiento por valor de mercado
print("[5/6] Valor de mercado vs G+A...")
fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(df_out["market_value_eur_M"], df_out["G+A"],
                c=df_out["xG"], cmap="YlOrRd", alpha=0.6, s=40, edgecolors="none")
plt.colorbar(sc, ax=ax, label="xG")
ax.set_xlabel("Valor de Mercado (M €)")
ax.set_ylabel("Goles + Asistencias")
ax.set_title("Rendimiento Ofensivo vs Valor de Mercado", fontsize=12, fontweight="bold")
save(fig, "05_valor_mercado_vs_ga")

# 3.6 Top 15 jugadores por G+A (outfield)
print("[6/6] Top 15 jugadores por G+A...")
top15 = df_out.nlargest(15, "G+A")[["Player","Pos","Comp","Gls","Ast","G+A","xG"]].reset_index(drop=True)
print(f"\nTop 15 jugadores por G+A:\n{top15.to_string()}")

fig, ax = plt.subplots(figsize=(11, 6))
bar = ax.barh(top15["Player"], top15["G+A"], color=sns.color_palette("RdYlGn", 15))
ax.set_xlabel("Goles + Asistencias")
ax.set_title("Top 15 Jugadores por Producción Ofensiva (G+A)", fontsize=12, fontweight="bold")
ax.invert_yaxis()
save(fig, "06_top15_jugadores_ga")


# ── 4. REGRESIÓN LINEAL MÚLTIPLE ──────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 4 — Modelado: Regresión Lineal Múltiple (predecir G+A)")
print("="*60)

features = ["xG", "xAG", "PrgP", "PrgC", "Min"]
X = df_out[features]
y = df_out["G+A"]

lr = LinearRegression()
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_r2   = cross_val_score(lr, X, y, cv=kf, scoring="r2")
cv_rmse = np.sqrt(-cross_val_score(lr, X, y, cv=kf, scoring="neg_mean_squared_error"))

lr.fit(X, y)
y_pred = lr.predict(X)

print(f"\n  Coeficientes:")
for feat, coef in zip(features, lr.coef_):
    print(f"    {feat:8s}: {coef:+.4f}")
print(f"  Intercepto: {lr.intercept_:.4f}")
print(f"\n  R² (CV 5-fold) : {cv_r2.mean():.4f}  ±  {cv_r2.std():.4f}")
print(f"  RMSE (CV)      : {cv_rmse.mean():.4f} ±  {cv_rmse.std():.4f}")
print(f"  MAE (train)    : {mean_absolute_error(y, y_pred):.4f}")
print(f"  R² (train)     : {r2_score(y, y_pred):.4f}")

# Gráfico residuos
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(y_pred, y - y_pred, alpha=0.4, s=20, color="#e74c3c")
axes[0].axhline(0, color="black", linewidth=1)
axes[0].set_xlabel("Valores predichos"); axes[0].set_ylabel("Residuos")
axes[0].set_title("Residuos — Regresión Lineal")

axes[1].scatter(y, y_pred, alpha=0.4, s=20, color="#3498db")
lim = [y.min()-1, y.max()+1]
axes[1].plot(lim, lim, "k--")
axes[1].set_xlabel("G+A real"); axes[1].set_ylabel("G+A predicho")
axes[1].set_title(f"Real vs Predicho  (R²={r2_score(y,y_pred):.3f})")
fig.suptitle("Evaluación Regresión Lineal — Predicción G+A", fontsize=13, fontweight="bold")
save(fig, "07_regresion_residuos")

# Random Forest (comparativa)
rf = RandomForestRegressor(n_estimators=100, random_state=42)
cv_r2_rf = cross_val_score(rf, X, y, cv=kf, scoring="r2")
rf.fit(X, y)
print(f"\n  Random Forest R² (CV): {cv_r2_rf.mean():.4f} ± {cv_r2_rf.std():.4f}")

# Importancia de variables (RF)
importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(8, 4))
importances.plot(kind="barh", ax=ax, color=sns.color_palette("Blues_r", len(features)))
ax.set_title("Importancia de Variables — Random Forest", fontsize=12, fontweight="bold")
ax.set_xlabel("Importancia relativa")
save(fig, "08_feature_importance_rf")


# ── 5. K-MEANS CLUSTERING ────────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 4 — Modelado: K-Means Clustering de perfiles de jugadores")
print("="*60)

cluster_features = ["Gls","Ast","xG","xAG","PrgC","PrgP","Min","G+A"]
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df_out[cluster_features])

# Elbow method
inertias, silhouettes = [], []
K_range = range(2, 9)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(K_range, inertias, "bo-", linewidth=2)
axes[0].set_xlabel("Número de clusters (k)")
axes[0].set_ylabel("Inercia")
axes[0].set_title("Elbow Method")
axes[1].plot(K_range, silhouettes, "ro-", linewidth=2)
axes[1].set_xlabel("Número de clusters (k)")
axes[1].set_ylabel("Silhouette Score")
axes[1].set_title("Silhouette Score por k")
fig.suptitle("Selección del Número Óptimo de Clusters", fontsize=13, fontweight="bold")
save(fig, "09_kmeans_elbow_silhouette")

best_k = K_range[np.argmax(silhouettes)]
print(f"\n  k óptimo (mayor Silhouette): {best_k}")
print(f"  Silhouette Score máximo   : {max(silhouettes):.4f}")

km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df_out["cluster"] = km_final.fit_predict(X_scaled)

# Perfil de cada cluster
cluster_profile = df_out.groupby("cluster")[cluster_features + ["Pos"]].agg(
    {col: "mean" for col in cluster_features} | {"Pos": lambda x: x.value_counts().index[0]}
).round(2)
print(f"\nPerfil de clusters:\n{cluster_profile.to_string()}")

# Etiquetas interpretables
cluster_labels = {
    i: f"Perfil {i+1}" for i in range(best_k)
}
# Asignar etiquetas basadas en G+A promedio
ga_means = df_out.groupby("cluster")["G+A"].mean().sort_values(ascending=False)
label_names = ["Delantero Goleador", "Mediocampista Creativo",
               "Defensor Ofensivo", "Jugador de Rotación",
               "Extremo Dinámico", "Mediocentro Defensivo"]
for rank, (cluster_id, _) in enumerate(ga_means.items()):
    cluster_labels[cluster_id] = label_names[rank % len(label_names)]
df_out["cluster_label"] = df_out["cluster"].map(cluster_labels)

# Scatter clusters (xG vs G+A)
fig, ax = plt.subplots(figsize=(10, 7))
palette = sns.color_palette("tab10", best_k)
for cid, grp in df_out.groupby("cluster"):
    ax.scatter(grp["xG"], grp["G+A"], label=cluster_labels[cid],
               alpha=0.5, s=35, color=palette[cid])
ax.set_xlabel("Expected Goals (xG)"); ax.set_ylabel("Goles + Asistencias")
ax.set_title(f"K-Means Clustering (k={best_k}) — Perfiles de Jugadores",
             fontsize=12, fontweight="bold")
ax.legend(title="Perfil", bbox_to_anchor=(1.01, 1), loc="upper left")
save(fig, "10_kmeans_clusters_scatter")


# ── 6. ÁRBOL DE DECISIÓN (clasificación over_xG) ────────────────────────────
print("\n" + "="*60)
print("FASE 4 — Modelado: Árbol de Decisión (¿supera el jugador su xG?)")
print("="*60)

dt_features = ["xG","xAG","PrgC","PrgP","Min","Age"]
Xc = df_out[dt_features]
yc = df_out["over_xG"]

dt = DecisionTreeClassifier(max_depth=4, random_state=42)
dt.fit(Xc, yc)
yc_pred = dt.predict(Xc)

cv_acc = cross_val_score(dt, Xc, yc, cv=kf, scoring="accuracy")
print(f"\n  Accuracy CV (5-fold): {cv_acc.mean():.4f} ± {cv_acc.std():.4f}")
print(f"\n  Reporte de clasificación:\n{classification_report(yc, yc_pred)}")
print(f"\n  Reglas del árbol (primeros niveles):")
print(export_text(dt, feature_names=dt_features, max_depth=3))

# Matriz de confusión
cm = confusion_matrix(yc, yc_pred)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
            xticklabels=["≤ xG", "> xG"], yticklabels=["≤ xG", "> xG"])
ax.set_xlabel("Predicho"); ax.set_ylabel("Real")
ax.set_title("Matriz de Confusión — Árbol de Decisión\n(¿supera el jugador su xG?)",
             fontsize=11, fontweight="bold")
save(fig, "11_confusion_matrix_dt")


# ── 7. EXPORTAR RESULTADOS PARA POWER BI ───────────────────────────────────
print("\n" + "="*60)
print("EXPORTACIÓN — CSV enriquecido para Power BI / Tableau")
print("="*60)

export_cols = ["Player","Nation","Pos","Squad","Comp","Age","Min","MP",
               "Gls","Ast","G+A","G-PK","PK","xG","xAG","npxG","npxG+xAG",
               "PrgC","PrgP","PrgR","Gls/90","Ast/90","xG/90",
               "CrdY","CrdR","over_xG","cluster","cluster_label",
               "market_value_eur_M"]
df_export = df_out[export_cols].copy()
df_export["GA_pred_lr"] = lr.predict(df_out[features]).round(2)
df_export["GA_pred_rf"] = rf.predict(df_out[features]).round(2)
df_export["xG_diff"]    = (df_out["Gls"] - df_out["xG"]).round(2)

out_path = "/home/claude/football-bigdata-project/data/football_stats_enriched.csv"
df_export.to_csv(out_path, index=False)
print(f"  Exportado → {out_path}")
print(f"  Registros: {len(df_export)} | Columnas: {len(df_export.columns)}")

# Resumen estadístico por liga
summary_liga = df_export.groupby("Comp").agg(
    jugadores=("Player","count"),
    goles_media=("Gls","mean"),
    asistencias_media=("Ast","mean"),
    xG_media=("xG","mean"),
    GA_media=("G+A","mean"),
    valor_medio_M=("market_value_eur_M","mean"),
    pct_over_xG=("over_xG","mean"),
).round(2)
summary_liga["pct_over_xG"] = (summary_liga["pct_over_xG"] * 100).round(1)
summary_liga.to_csv("/home/claude/football-bigdata-project/data/summary_by_league.csv")
print(f"\nResumen por liga:\n{summary_liga.to_string()}")

print("\n" + "="*60)
print("✅  ANÁLISIS COMPLETO — Todos los artefactos generados")
print("="*60)
