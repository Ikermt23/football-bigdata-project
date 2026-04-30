"""
01_eda_and_modeling.py — Proyecto Final Big Data Football Players Stats 2024-2025
Dataset real: Kaggle/FBref (2854 registros, 267 columnas)
"""
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, warnings
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, r2_score, classification_report, confusion_matrix, silhouette_score

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "docs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save(fig, name):
    p = OUTPUT_DIR / f"{name}.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] -> {p}")

# ── 1. CARGA ──────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 2 - Comprension de los datos")
print("="*60)

df = pd.read_csv(DATA_DIR / "football_stats_2024_25.csv")
print(f"\nRegistros cargados : {len(df)}")
print(f"Columnas totales   : {len(df.columns)}")

KEY_COLS = [c for c in ["Age","Min","Gls","Ast","xG","xAG","G+A"] if c in df.columns]
print(f"\nEstadistica descriptiva (variables clave):")
print(df[KEY_COLS].describe().round(2).to_string())

nulos = df.isnull().sum(); nulos = nulos[nulos > 0]
print(f"\nTop 10 columnas con nulos:")
print(nulos.sort_values(ascending=False).head(10).to_string())

# ── 2. LIMPIEZA ───────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 3 - Preparacion de los datos")
print("="*60)

df["Pos"] = df["Pos"].astype(str).str.split(",").str[0].str.strip()
print(f"\nPosiciones unicas: {sorted(df['Pos'].unique())}")

df_gk  = df[df["Pos"] == "GK"].copy()
df_out = df[df["Pos"] != "GK"].copy()
print(f"Porteros separados : {len(df_gk)}")
print(f"Jugadores de campo : {len(df_out)}")

df_out = df_out[df_out["Min"] >= 90].copy()
print(f"Tras filtrar <90 min: {len(df_out)} jugadores")

df_out["Age"] = pd.to_numeric(df_out["Age"], errors="coerce")

if "Gls/90" not in df_out.columns:
    divisor = pd.to_numeric(df_out.get("90s", df_out["Min"]/90), errors="coerce").replace(0, np.nan)
    df_out["Gls/90"] = (df_out["Gls"] / divisor).round(3)
    df_out["Ast/90"] = (df_out["Ast"] / divisor).round(3)
    df_out["xG/90"]  = (df_out["xG"]  / divisor).round(3)
    print("  Columnas /90 calculadas")

base_val = df_out["Pos"].map({"DF":12,"MF":18,"FW":25}).fillna(15)
df_out["market_value_eur_M"] = (
    base_val * (1 + df_out["Gls"]*0.3 + df_out["Ast"]*0.15 + df_out["xG"]*0.1)
).clip(0.5, 200).round(1)
print(f"  market_value_eur_M estimada: {df_out['market_value_eur_M'].min()}M - {df_out['market_value_eur_M'].max()}M")

for col in ["xG","xAG","npxG","npxG+xAG","PrgC","PrgP","PrgR","Gls/90","Ast/90","xG/90","Age"]:
    if col in df_out.columns:
        df_out[col] = pd.to_numeric(df_out[col], errors="coerce").fillna(df_out[col].median())

df_out["over_xG"] = (df_out["Gls"] > df_out["xG"]).astype(int)
print(f"\nJugadores que superan su xG: {df_out['over_xG'].sum()} ({df_out['over_xG'].mean()*100:.1f}%)")
print(f"Dataset limpio: {len(df_out)} jugadores")

# ── 3. EDA ────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 2 - EDA")
print("="*60)

pos_ok  = ["DF","MF","FW"]
df_plot = df_out[df_out["Pos"].isin(pos_ok)].copy()

print("\n[1/6] Boxplots por posicion...")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Distribucion de Variables Ofensivas por Posicion", fontsize=14, fontweight="bold")
for ax, col, title in zip(axes, ["Gls","Ast","G+A"], ["Goles","Asistencias","G+A"]):
    sns.boxplot(data=df_plot, x="Pos", y=col, ax=ax, order=pos_ok, palette="Set2")
    ax.set_title(title); ax.set_xlabel("Posicion"); ax.set_ylabel(col)
save(fig, "01_distribucion_goles_posicion")

print("[2/6] Gls/90 por liga...")
df_plot["Comp_c"] = df_plot["Comp"].str.replace("Premier League","Premier L.")
orden = df_plot.groupby("Comp_c")["Gls/90"].median().sort_values(ascending=False).index
fig, ax = plt.subplots(figsize=(12, 5))
sns.boxplot(data=df_plot, x="Comp_c", y="Gls/90", order=orden, palette="coolwarm", ax=ax)
ax.set_title("Goles/90 min por Liga", fontsize=13, fontweight="bold")
ax.set_xlabel("Liga"); ax.set_ylabel("Goles/90")
plt.xticks(rotation=15)
save(fig, "02_goles90_por_liga")

print("[3/6] Heatmap correlaciones...")
cc = [c for c in ["Gls","Ast","G+A","xG","xAG","npxG","npxG+xAG","Min","PrgC","PrgP","PrgR","CrdY","market_value_eur_M"] if c in df_out.columns]
corr = df_out[cc].corr()
fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(corr, mask=np.triu(np.ones_like(corr,dtype=bool)), annot=True, fmt=".2f",
            cmap="RdYlGn", center=0, linewidths=0.5, ax=ax, annot_kws={"size":8})
ax.set_title("Matriz de Correlacion", fontsize=13, fontweight="bold")
save(fig, "03_heatmap_correlaciones")

print("[4/6] Scatter xG vs Goles...")
fig, ax = plt.subplots(figsize=(9, 7))
for pos, grp in df_plot.groupby("Pos"):
    ax.scatter(grp["xG"], grp["Gls"], alpha=0.45, s=25,
               label=pos, color={"DF":"#3498db","MF":"#2ecc71","FW":"#e74c3c"}.get(pos,"gray"))
lm = df_plot[["xG","Gls"]].max().max() + 2
ax.plot([0,lm],[0,lm],"k--",linewidth=1.2,label="xG=Goles")
ax.set_xlim([0,lm]); ax.set_ylim([0,lm])
ax.set_xlabel("xG"); ax.set_ylabel("Goles")
ax.set_title("Goles Reales vs xG", fontsize=12, fontweight="bold")
ax.legend()
save(fig, "04_scatter_xg_vs_goles")

print("[5/6] Valor estimado vs G+A...")
fig, ax = plt.subplots(figsize=(9, 6))
sc = ax.scatter(df_out["market_value_eur_M"], df_out["G+A"],
                c=df_out["xG"], cmap="YlOrRd", alpha=0.55, s=35, edgecolors="none")
plt.colorbar(sc, ax=ax, label="xG")
ax.set_xlabel("Valor Estimado (M EUR)"); ax.set_ylabel("G+A")
ax.set_title("Rendimiento vs Valor Estimado de Mercado", fontsize=12, fontweight="bold")
save(fig, "05_valor_mercado_vs_ga")

print("[6/6] Top 15...")
top15 = df_out[df_out["Min"]>=450].nlargest(15,"G+A")[["Player","Pos","Comp","Gls","Ast","G+A","xG"]].reset_index(drop=True)
print(f"\n{top15.to_string()}")
fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(top15["Player"], top15["G+A"], color=sns.color_palette("RdYlGn", len(top15)))
ax.set_xlabel("G+A"); ax.set_title("Top 15 Jugadores por G+A", fontsize=12, fontweight="bold")
ax.invert_yaxis()
save(fig, "06_top15_jugadores_ga")

# ── 4. MODELOS ML ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("FASE 4 - Modelado")
print("="*60)

features = ["xG","xAG","PrgP","PrgC","Min"]
for f in features:
    df_out[f] = pd.to_numeric(df_out[f], errors="coerce").fillna(0)
X = df_out[features]; y = df_out["G+A"]
kf = KFold(n_splits=5, shuffle=True, random_state=42)

lr = LinearRegression()
cv_r2   = cross_val_score(lr, X, y, cv=kf, scoring="r2")
cv_rmse = np.sqrt(-cross_val_score(lr, X, y, cv=kf, scoring="neg_mean_squared_error"))
lr.fit(X, y); y_pred = lr.predict(X)
print(f"\n--- Regresion Lineal ---")
for f, c in zip(features, lr.coef_): print(f"  {f:8s}: {c:+.4f}")
print(f"  R2 CV (k=5): {cv_r2.mean():.4f} +/- {cv_r2.std():.4f}")
print(f"  RMSE CV    : {cv_rmse.mean():.4f} +/- {cv_rmse.std():.4f}")
print(f"  MAE train  : {mean_absolute_error(y,y_pred):.4f}")
print(f"  R2 train   : {r2_score(y,y_pred):.4f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(y_pred, y-y_pred, alpha=0.35, s=18, color="#e74c3c")
axes[0].axhline(0, color="black", linewidth=1)
axes[0].set_xlabel("Predicho"); axes[0].set_ylabel("Residuos"); axes[0].set_title("Residuos")
axes[1].scatter(y, y_pred, alpha=0.35, s=18, color="#3498db")
lim = [y.min()-1, y.max()+1]; axes[1].plot(lim,lim,"k--")
axes[1].set_xlabel("Real"); axes[1].set_ylabel("Predicho")
axes[1].set_title(f"Real vs Predicho (R2={r2_score(y,y_pred):.3f})")
fig.suptitle("Regresion Lineal - Prediccion G+A", fontsize=13, fontweight="bold")
save(fig, "07_regresion_residuos")

rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
cv_r2_rf = cross_val_score(rf, X, y, cv=kf, scoring="r2")
rf.fit(X, y)
print(f"\n--- Random Forest ---")
print(f"  R2 CV (k=5): {cv_r2_rf.mean():.4f} +/- {cv_r2_rf.std():.4f}")
imp = pd.Series(rf.feature_importances_, index=features).sort_values()
fig, ax = plt.subplots(figsize=(8, 4))
imp.plot(kind="barh", ax=ax, color=sns.color_palette("Blues_r", len(features)))
ax.set_title("Importancia de Variables - Random Forest", fontsize=12, fontweight="bold")
save(fig, "08_feature_importance_rf")

# K-Means
cluster_features = ["Gls","Ast","xG","xAG","PrgC","PrgP","Min","G+A"]
X_scaled = MinMaxScaler().fit_transform(df_out[cluster_features])
inertias, silhouettes = [], []
for k in range(2, 9):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    lb = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, lb))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(range(2,9), inertias, "bo-", linewidth=2)
axes[0].set_xlabel("k"); axes[0].set_ylabel("Inercia"); axes[0].set_title("Elbow")
axes[1].plot(range(2,9), silhouettes, "ro-", linewidth=2)
axes[1].set_xlabel("k"); axes[1].set_ylabel("Silhouette"); axes[1].set_title("Silhouette Score")
fig.suptitle("Seleccion Numero Optimo de Clusters", fontsize=13, fontweight="bold")
save(fig, "09_kmeans_elbow_silhouette")

best_k = list(range(2,9))[int(np.argmax(silhouettes))]
print(f"\n--- K-Means (k={best_k}, Silhouette={max(silhouettes):.4f}) ---")
km_f = KMeans(n_clusters=best_k, random_state=42, n_init=10)
df_out["cluster"] = km_f.fit_predict(X_scaled)
prof = df_out.groupby("cluster")[cluster_features+["Pos"]].agg(
    {c:"mean" for c in cluster_features}|{"Pos": lambda x: x.value_counts().index[0]}).round(2)
print(prof.to_string())
lbl_names = ["Delantero Goleador","Mediocampista Creativo","Defensor Ofensivo","Jugador Rotacion","Extremo Dinamico","Mediocentro Defensivo"]
ga_m = df_out.groupby("cluster")["G+A"].mean().sort_values(ascending=False)
cl = {cid: lbl_names[r % len(lbl_names)] for r,(cid,_) in enumerate(ga_m.items())}
df_out["cluster_label"] = df_out["cluster"].map(cl)
fig, ax = plt.subplots(figsize=(10, 7))
pal = sns.color_palette("tab10", best_k)
for cid, grp in df_out.groupby("cluster"):
    ax.scatter(grp["xG"], grp["G+A"], label=cl[cid], alpha=0.45, s=30, color=pal[cid])
ax.set_xlabel("xG"); ax.set_ylabel("G+A")
ax.set_title(f"K-Means (k={best_k}) - Perfiles de Jugadores", fontsize=12, fontweight="bold")
ax.legend(title="Perfil", bbox_to_anchor=(1.01,1), loc="upper left")
save(fig, "10_kmeans_clusters_scatter")

# Arbol Decision
dt_features = ["xG","xAG","PrgC","PrgP","Min","Age"]
for f in dt_features:
    df_out[f] = pd.to_numeric(df_out[f], errors="coerce").fillna(0)
Xc = df_out[dt_features]; yc = df_out["over_xG"]
dt = DecisionTreeClassifier(max_depth=4, random_state=42)
dt.fit(Xc, yc); yc_pred = dt.predict(Xc)
cv_acc = cross_val_score(dt, Xc, yc, cv=kf, scoring="accuracy")
print(f"\n--- Arbol de Decision ---")
print(f"  Accuracy CV: {cv_acc.mean():.4f} +/- {cv_acc.std():.4f}")
print(classification_report(yc, yc_pred))
print(export_text(dt, feature_names=dt_features, max_depth=3))
cm = confusion_matrix(yc, yc_pred)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
            xticklabels=["<=xG",">xG"], yticklabels=["<=xG",">xG"])
ax.set_xlabel("Predicho"); ax.set_ylabel("Real"); ax.set_title("Matriz de Confusion - Arbol Decision")
save(fig, "11_confusion_matrix_dt")

# ── 5. EXPORTAR ───────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("EXPORTACION - CSV para Power BI")
print("="*60)
b = ["Player","Nation","Pos","Squad","Comp","Age","Min","MP","Gls","Ast","G+A","G-PK","PK","xG","xAG","npxG","npxG+xAG","PrgC","PrgP","PrgR","CrdY","CrdR"]
c = ["Gls/90","Ast/90","xG/90","market_value_eur_M","over_xG","cluster","cluster_label"]
ecols = [col for col in b+c if col in df_out.columns]
df_exp = df_out[ecols].copy()
df_exp["GA_pred_lr"] = lr.predict(df_out[features]).round(2)
df_exp["GA_pred_rf"] = rf.predict(df_out[features]).round(2)
df_exp["xG_diff"]    = (df_out["Gls"] - df_out["xG"]).round(2)
df_exp.to_csv(DATA_DIR / "football_stats_enriched.csv", index=False)
print(f"  Exportado: {len(df_exp)} registros, {len(df_exp.columns)} columnas")

sl = df_exp.groupby("Comp").agg(
    jugadores=("Player","count"), goles_media=("Gls","mean"), xG_media=("xG","mean"),
    GA_media=("G+A","mean"), valor_medio_M=("market_value_eur_M","mean"), pct_over_xG=("over_xG","mean")
).round(2)
sl["pct_over_xG"] = (sl["pct_over_xG"]*100).round(1)
sl.to_csv(DATA_DIR / "summary_by_league.csv")
print(f"\nResumen por liga:\n{sl.to_string()}")
print("\n" + "="*60)
print("ANALISIS COMPLETO")
print("="*60)
