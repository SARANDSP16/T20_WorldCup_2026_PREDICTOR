import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

table2_path = BASE / "processed" / "table2_match_by_match.csv"
table1_path = BASE / "processed" / "table1_player_career.csv"
out_path = BASE / "processed" / "table3_player_vs_opponent.csv"

print("📂 Loading Table-2:", table2_path)
df = pd.read_csv(table2_path)

print("📂 Loading Table-1:", table1_path)
table1 = pd.read_csv(table1_path)

# ---------------------------------------------------------
# Clean names
# ---------------------------------------------------------
for col in ["batter", "bowler", "fielder", "player_out", "batting_team"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# ---------------------------------------------------------
# ONLY 385 PLAYERS
# ---------------------------------------------------------
valid_players = set(table1["player_full_name"])

# ---------------------------------------------------------
# Create opponent_team (IMPORTANT FIX)
# ---------------------------------------------------------
# For batting stats → bowler's team is opponent
df["opponent_team_bat"] = df["bowler"].map(
    dict(zip(table1["player_full_name"], table1["team"]))
)

# For bowling stats → batter's team is opponent
df["opponent_team_bowl"] = df["batter"].map(
    dict(zip(table1["player_full_name"], table1["team"]))
)

# ---------------------------------------------------------
# Batting Aggregates vs Opponent
# ---------------------------------------------------------
bat_df = df[df["batter"].isin(valid_players)]

bat_group = (
    bat_df.groupby(["batter", "opponent_team_bat"], as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        runs=("runs_batter", "sum"),
        balls=("runs_batter", "count"),
        fours=("four", "sum"),
        sixes=("six", "sum"),
        dismissals=("player_out", lambda x: x.notna().sum()),
    )
)

bat_group["strike_rate"] = ((bat_group["runs"] / bat_group["balls"]) * 100).round(2)
bat_group["avg"] = (
    bat_group["runs"] / bat_group["dismissals"].replace(0, None)
).round(2)

bat_group.rename(columns={"batter": "player_name", "opponent_team_bat": "opponent_team"}, inplace=True)

# ---------------------------------------------------------
# Bowling Aggregates vs Opponent
# ---------------------------------------------------------
bowl_df = df[df["bowler"].isin(valid_players)]

bowl_group = (
    bowl_df.groupby(["bowler", "opponent_team_bowl"], as_index=False)
    .agg(
        matches=("match_id", "nunique"),
        balls=("runs_total", "count"),
        runs_conceded=("runs_total", "sum"),
        wickets=("player_out", lambda x: x.notna().sum())
    )
)

bowl_group["economy"] = (bowl_group["runs_conceded"] / (bowl_group["balls"] / 6)).round(2)
bowl_group["avg"] = (
    bowl_group["runs_conceded"] / bowl_group["wickets"].replace(0, None)
).round(2)

bowl_group.rename(columns={"bowler": "player_name", "opponent_team_bowl": "opponent_team"}, inplace=True)

# ---------------------------------------------------------
# Merge batting + bowling
# ---------------------------------------------------------
final = pd.merge(
    bat_group,
    bowl_group,
    on=["player_name", "opponent_team"],
    how="outer",
    suffixes=("_bat", "_bowl")
).fillna(0)

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------
final.to_csv(out_path, index=False)

print("\n🎉 Table-3 Player vs Opponent Saved →", out_path)
print("📦 Total rows:", len(final))
