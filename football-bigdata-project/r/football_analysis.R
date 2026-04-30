# ============================================================
# Football Players Stats 2024-2025
# Análisis con R — Tidyverse (dplyr + ggplot2)
# Proyecto Final Big Data e IA — España 2024-2025
# ============================================================
# Instalación (ejecutar una vez):
#   install.packages(c("tidyverse", "corrplot", "ggrepel", "scales"))
# ============================================================

library(tidyverse)   # dplyr, ggplot2, tidyr, readr, forcats
library(corrplot)    # heatmap de correlaciones
library(ggrepel)     # etiquetas sin solapamiento en scatter
library(scales)      # formato numérico en ejes

# ------------------------------------------------------------
# 1. CARGA DE DATOS
# ------------------------------------------------------------

df_raw <- read_csv("../data/football_stats_2024_25.csv",
                   show_col_types = FALSE)

cat("=== DIAGNÓSTICO INICIAL ===\n")
cat("Filas:", nrow(df_raw), "| Columnas:", ncol(df_raw), "\n")
cat("Valores NA por columna:\n")
print(colSums(is.na(df_raw)))

glimpse(df_raw)

# ------------------------------------------------------------
# 2. LIMPIEZA Y PREPARACIÓN
# ------------------------------------------------------------

df_field <- df_raw |>
  filter(Pos != "GK", Min >= 90) |>
  mutate(
    over_xG      = if_else(Gls > xG, 1L, 0L),
    xG_diff      = Gls - xG,
    GA_per90     = (`G+A` / Min) * 90,
    Comp         = as_factor(Comp),
    Pos          = as_factor(Pos)
  )

cat("\nJugadores de campo con Min >= 90:", nrow(df_field), "\n")
cat("Distribución de posiciones:\n")
print(count(df_field, Pos, sort = TRUE))

# ------------------------------------------------------------
# 3. ESTADÍSTICA DESCRIPTIVA — dplyr
# ------------------------------------------------------------

cat("\n=== ESTADÍSTICAS POR LIGA ===\n")

resumen_liga <- df_field |>
  group_by(Comp) |>
  summarise(
    n_jugadores    = n(),
    media_GA       = round(mean(`G+A`), 2),
    mediana_GA     = round(median(`G+A`), 2),
    media_xG       = round(mean(xG), 2),
    sd_GA          = round(sd(`G+A`), 2),
    pct_over_xG    = round(mean(over_xG) * 100, 1),
    media_valor_M  = round(mean(market_value_eur_M, na.rm = TRUE), 1),
    .groups = "drop"
  ) |>
  arrange(desc(media_GA))

print(resumen_liga)

cat("\n=== TOP 15 JUGADORES POR G+A ===\n")

top15 <- df_field |>
  slice_max(`G+A`, n = 15) |>
  select(Player, Squad, Comp, Pos, Gls, Ast, `G+A`, xG, xG_diff) |>
  arrange(desc(`G+A`))

print(top15)

# ------------------------------------------------------------
# 4. ANÁLISIS DE CORRELACIÓN
# ------------------------------------------------------------

vars_numericas <- df_field |>
  select(Gls, Ast, `G+A`, xG, xAG, `npxG+xAG`, PrgC, PrgP, Min,
         market_value_eur_M) |>
  drop_na()

cor_matrix <- cor(vars_numericas, method = "pearson")

cat("\n=== CORRELACIONES CON G+A ===\n")
cor_con_GA <- sort(cor_matrix[, "G+A"], decreasing = TRUE)
print(round(cor_con_GA, 3))

# Guardar heatmap de correlaciones
png("../docs/figures/R_01_heatmap_correlaciones.png",
    width = 900, height = 800, res = 120)
corrplot(cor_matrix,
         method  = "color",
         type    = "upper",
         tl.cex  = 0.8,
         addCoef.col = "black",
         number.cex  = 0.65,
         title   = "Matriz de correlación — Football Stats 2024-25",
         mar     = c(0, 0, 1.5, 0))
dev.off()

# ------------------------------------------------------------
# 5. ANOVA — Diferencias entre ligas en Gls/90
# ------------------------------------------------------------

cat("\n=== ANOVA: Gls/90 por liga ===\n")

modelo_anova <- aov(`Gls/90` ~ Comp, data = df_field)
print(summary(modelo_anova))

# Post-hoc Tukey
tukey <- TukeyHSD(modelo_anova)
cat("\nComparaciones Tukey HSD (p-value ajustado):\n")
print(tukey)

# Guardar boxplot Gls/90 por liga
p_anova <- df_field |>
  ggplot(aes(x = fct_reorder(Comp, `Gls/90`, .fun = median, .desc = TRUE),
             y = `Gls/90`, fill = Comp)) +
  geom_boxplot(outlier.size = 1, alpha = 0.8) +
  labs(
    title    = "Distribución de Goles/90 por Liga",
    subtitle = "ANOVA con post-hoc Tukey — Temporada 2024-25",
    x        = NULL,
    y        = "Goles por 90 minutos",
    caption  = "Fuente: FBref / Kaggle (Sidorowicz, 2024)"
  ) +
  scale_fill_brewer(palette = "Set2") +
  theme_minimal(base_size = 13) +
  theme(legend.position = "none",
        plot.title = element_text(face = "bold"))

ggsave("../docs/figures/R_02_anova_goles90_liga.png",
       p_anova, width = 10, height = 6, dpi = 150)

# ------------------------------------------------------------
# 6. VISUALIZACIÓN — Scatter xG vs Goles por posición
# ------------------------------------------------------------

p_scatter <- df_field |>
  filter(xG > 0.5) |>
  ggplot(aes(x = xG, y = Gls, colour = Pos)) +
  geom_point(alpha = 0.55, size = 1.8) +
  geom_abline(slope = 1, intercept = 0,
              linetype = "dashed", colour = "grey40", linewidth = 0.8) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 1.1) +
  labs(
    title    = "Expected Goals vs Goles reales por posición",
    subtitle = "Línea discontinua = xG perfectamente convertido",
    x        = "Expected Goals (xG)",
    y        = "Goles marcados",
    colour   = "Posición",
    caption  = "Fuente: FBref / Kaggle (Sidorowicz, 2024)"
  ) +
  scale_colour_brewer(palette = "Dark2") +
  theme_minimal(base_size = 13) +
  theme(plot.title = element_text(face = "bold"))

ggsave("../docs/figures/R_03_scatter_xg_goles.png",
       p_scatter, width = 10, height = 6, dpi = 150)

# ------------------------------------------------------------
# 7. TOP 15 JUGADORES — Gráfico de barras horizontales
# ------------------------------------------------------------

p_top15 <- top15 |>
  mutate(Player = fct_reorder(Player, `G+A`)) |>
  ggplot(aes(x = `G+A`, y = Player, fill = Pos)) +
  geom_col(alpha = 0.85) +
  geom_text(aes(label = `G+A`), hjust = -0.2, size = 3.5) +
  scale_fill_brewer(palette = "Set1") +
  labs(
    title   = "Top 15 jugadores por Goles + Asistencias",
    x       = "G+A",
    y       = NULL,
    fill    = "Posición",
    caption = "Fuente: FBref / Kaggle (Sidorowicz, 2024)"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold")) +
  xlim(0, max(top15$`G+A`) * 1.1)

ggsave("../docs/figures/R_04_top15_GA.png",
       p_top15, width = 10, height = 7, dpi = 150)

# ------------------------------------------------------------
# 8. DISTRIBUCIÓN G+A POR POSICIÓN — Violin + Jitter
# ------------------------------------------------------------

p_violin <- df_field |>
  filter(Pos != "GK") |>
  ggplot(aes(x = Pos, y = `G+A`, fill = Pos)) +
  geom_violin(trim = FALSE, alpha = 0.6) +
  geom_jitter(width = 0.15, alpha = 0.25, size = 0.9) +
  stat_summary(fun = median, geom = "point",
               shape = 23, size = 3, fill = "white") +
  scale_fill_brewer(palette = "Pastel1") +
  labs(
    title    = "Distribución de G+A por posición",
    subtitle = "Diamante blanco = mediana",
    x        = "Posición",
    y        = "Goles + Asistencias",
    caption  = "Fuente: FBref / Kaggle (Sidorowicz, 2024)"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "none",
        plot.title = element_text(face = "bold"))

ggsave("../docs/figures/R_05_violin_GA_posicion.png",
       p_violin, width = 9, height = 6, dpi = 150)

# ------------------------------------------------------------
# 9. OUTPERFORMERS — Jugadores que superan más su xG
# ------------------------------------------------------------

cat("\n=== TOP OUTPERFORMERS (Gls - xG) ===\n")

outperformers <- df_field |>
  filter(xG >= 3) |>
  slice_max(xG_diff, n = 10) |>
  select(Player, Squad, Comp, Pos, Gls, xG, xG_diff)

print(outperformers)

p_outperf <- outperformers |>
  mutate(Player = fct_reorder(Player, xG_diff)) |>
  ggplot(aes(x = xG_diff, y = Player, fill = Pos)) +
  geom_col(alpha = 0.85) +
  geom_text(aes(label = round(xG_diff, 1)), hjust = -0.2, size = 3.5) +
  scale_fill_brewer(palette = "Set2") +
  labs(
    title   = "Top outperformers — Goles por encima del xG",
    x       = "Goles - xG",
    y       = NULL,
    fill    = "Posición",
    caption = "Fuente: FBref / Kaggle (Sidorowicz, 2024). Filtro: xG >= 3"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold")) +
  xlim(0, max(outperformers$xG_diff) * 1.15)

ggsave("../docs/figures/R_06_outperformers_xG.png",
       p_outperf, width = 10, height = 6, dpi = 150)

# ------------------------------------------------------------
# 10. RESUMEN FINAL
# ------------------------------------------------------------

cat("\n=== RESUMEN FINAL ===\n")
cat("Figuras guardadas en docs/figures/:\n")
cat("  R_01_heatmap_correlaciones.png\n")
cat("  R_02_anova_goles90_liga.png\n")
cat("  R_03_scatter_xg_goles.png\n")
cat("  R_04_top15_GA.png\n")
cat("  R_05_violin_GA_posicion.png\n")
cat("  R_06_outperformers_xG.png\n")
cat("\nCorrelación más alta con G+A:", names(cor_con_GA)[2], "=",
    round(cor_con_GA[2], 3), "\n")
cat("Ligas ordenadas por G+A medio:\n")
print(select(resumen_liga, Comp, media_GA, pct_over_xG))
