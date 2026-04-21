"""
generate_sample_data.py
Genera un dataset simulado realista basado en la estructura del dataset
"Football Players Stats 2024-2025" de Kaggle (FBref).
Usado para desarrollo y pruebas sin necesidad de descargar el dataset original.
"""

import pandas as pd
import numpy as np

np.random.seed(42)

LEAGUES = {
    "Premier League": ["Arsenal", "Chelsea", "Liverpool", "Man City", "Man United",
                       "Tottenham", "Newcastle", "Aston Villa", "Brighton", "West Ham"],
    "La Liga":        ["Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla",
                       "Athletic Club", "Real Sociedad", "Valencia", "Villarreal", "Betis", "Osasuna"],
    "Bundesliga":     ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen",
                       "Eintracht Frankfurt", "Wolfsburg", "Freiburg", "Stuttgart", "Mainz", "Union Berlin"],
    "Serie A":        ["Inter Milan", "AC Milan", "Juventus", "Napoli", "Roma",
                       "Lazio", "Fiorentina", "Atalanta", "Torino", "Bologna"],
    "Ligue 1":        ["PSG", "Monaco", "Marseille", "Lyon", "Lille",
                       "Nice", "Rennes", "Lens", "Strasbourg", "Nantes"],
}

POSITIONS   = ["GK", "DF", "MF", "FW"]
POS_WEIGHTS = [0.08, 0.35, 0.35, 0.22]

NATIONS = ["ESP", "FRA", "GER", "ENG", "ITA", "POR", "ARG", "BRA",
           "NED", "BEL", "URU", "COL", "SEN", "NGR", "MAR", "CRO", "POL"]

def generate_player_name(idx):
    first = ["Luca", "Marco", "James", "Carlos", "Luis", "Antoine", "Kai",
             "Jude", "Vinicius", "Erling", "Kylian", "Pedri", "Gavi", "Bukayo",
             "Trent", "Phil", "Harry", "Son", "Bruno", "Kevin", "Robert"]
    last  = ["Smith", "Garcia", "Müller", "Rossi", "Dupont", "Silva", "Santos",
             "López", "Fernández", "Martinez", "Rodríguez", "Hernández", "González",
             "Pérez", "Wagner", "Becker", "Fischer", "Schneider", "Meyer", "Weber"]
    return f"{first[idx % len(first)]} {last[(idx * 7) % len(last)]} {idx}"

rows = []
player_idx = 0

for comp, squads in LEAGUES.items():
    for squad in squads:
        n_players = np.random.randint(18, 26)
        for _ in range(n_players):
            pos = np.random.choice(POSITIONS, p=POS_WEIGHTS)
            age = int(np.random.normal(26, 4))
            age = max(17, min(38, age))

            mp     = np.random.randint(5, 34)
            starts = np.random.randint(0, mp + 1)
            min_played = starts * np.random.randint(45, 90) + (mp - starts) * np.random.randint(10, 45)
            min_played = max(0, min_played)

            # Producción ofensiva según posición
            if pos == "GK":
                gls, ast, xg, xag = 0, 0, 0.0, 0.0
                prgc, prgp, prgr = 0, np.random.randint(0, 30), np.random.randint(0, 10)
            elif pos == "DF":
                gls  = np.random.poisson(1.2)
                ast  = np.random.poisson(1.8)
                xg   = round(np.random.exponential(1.5), 2)
                xag  = round(np.random.exponential(1.8), 2)
                prgc = np.random.randint(10, 80)
                prgp = np.random.randint(20, 150)
                prgr = np.random.randint(10, 80)
            elif pos == "MF":
                gls  = np.random.poisson(4)
                ast  = np.random.poisson(6)
                xg   = round(np.random.exponential(4.0), 2)
                xag  = round(np.random.exponential(5.0), 2)
                prgc = np.random.randint(30, 150)
                prgp = np.random.randint(50, 300)
                prgr = np.random.randint(40, 180)
            else:  # FW
                gls  = np.random.poisson(10)
                ast  = np.random.poisson(5)
                xg   = round(np.random.exponential(9.0), 2)
                xag  = round(np.random.exponential(4.5), 2)
                prgc = np.random.randint(40, 200)
                prgp = np.random.randint(20, 120)
                prgr = np.random.randint(60, 220)

            pk      = np.random.poisson(0.5) if pos == "FW" else 0
            pkatt   = pk + (1 if np.random.random() < 0.2 else 0)
            g_pk    = max(0, gls - pk)
            npxg    = round(max(0, xg - pk * 0.76), 2)
            npxg_xag = round(npxg + xag, 2)
            ga      = gls + ast

            crdy = np.random.poisson(3 if pos in ["DF", "MF"] else 1)
            crdr = 1 if np.random.random() < 0.03 else 0

            mins90 = min_played / 90 if min_played > 0 else 0.001
            gls90  = round(gls / mins90, 2) if mins90 > 0 else 0.0
            ast90  = round(ast / mins90, 2) if mins90 > 0 else 0.0
            xg90   = round(xg / mins90, 2) if mins90 > 0 else 0.0

            # Valor de mercado simulado (millones EUR)
            base_val = {"GK": 8, "DF": 12, "MF": 18, "FW": 25}[pos]
            market_value = round(
                base_val * (1 + gls * 0.3 + ast * 0.15 + xg * 0.1) *
                np.random.uniform(0.5, 2.0), 1
            )
            market_value = max(0.5, min(200.0, market_value))

            rows.append({
                "Player":      generate_player_name(player_idx),
                "Nation":      np.random.choice(NATIONS),
                "Pos":         pos,
                "Squad":       squad,
                "Comp":        comp,
                "Age":         age,
                "MP":          mp,
                "Starts":      starts,
                "Min":         min_played,
                "Gls":         gls,
                "Ast":         ast,
                "G+A":         ga,
                "G-PK":        g_pk,
                "PK":          pk,
                "PKatt":       pkatt,
                "CrdY":        crdy,
                "CrdR":        crdr,
                "xG":          xg,
                "npxG":        npxg,
                "xAG":         xag,
                "npxG+xAG":    npxg_xag,
                "PrgC":        prgc,
                "PrgP":        prgp,
                "PrgR":        prgr,
                "Gls/90":      gls90,
                "Ast/90":      ast90,
                "xG/90":       xg90,
                "market_value_eur_M": market_value,
            })
            player_idx += 1

df = pd.DataFrame(rows)
df.to_csv("/home/claude/football-bigdata-project/data/football_stats_2024_25.csv", index=False)
print(f"Dataset generado: {len(df)} jugadores, {len(df.columns)} columnas")
print(df.head(3).to_string())
