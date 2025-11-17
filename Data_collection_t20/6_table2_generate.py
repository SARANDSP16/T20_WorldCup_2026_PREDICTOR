import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

deliveries_path = BASE / "outputs" / "deliveries.csv"
matches_path = BASE / "outputs" / "matches.csv"
table1_path = BASE / "processed" / "table1_player_career.csv"

processed_dir = BASE / "processed"
processed_dir.mkdir(exist_ok=True)

out_file = processed_dir / "table2_match_by_match.csv"

print("📂 Loading deliveries:", deliveries_path)
df = pd.read_csv(deliveries_path)

print("📂 Loading matches:", matches_path)
matches_df = pd.read_csv(matches_path)

print("📂 Loading Table-1 players:", table1_path)
table1_df = pd.read_csv(table1_path)

# -------------------------------------------------------------------
# Filter only Table-1 players
# -------------------------------------------------------------------
valid_players = set(table1_df["player_full_name"].astype(str).str.strip())

for col in ["batter", "bowler", "fielder", "player_out", "non_striker", "batting_team"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

filtered = df[
    df["batter"].isin(valid_players)
    | df["bowler"].isin(valid_players)
    | df["fielder"].isin(valid_players)
    | df["player_out"].isin(valid_players)
]

print("✅ Deliveries kept (after filtering by Table-1 players):", len(filtered))

# -------------------------------------------------------------------
# Merge match metadata
# -------------------------------------------------------------------
full = filtered.merge(matches_df, on="match_id", how="left")

# -------------------------------------------------------------------
# Boundary flags
# -------------------------------------------------------------------
full["four"] = (full["runs_batter"] == 4).astype(int)
full["six"] = (full["runs_batter"] == 6).astype(int)

# -------------------------------------------------------------------
# Ball type
# -------------------------------------------------------------------
def ball_type(row):
    if row["wide"] > 0:
        return "wide"
    if row["noball"] > 0:
        return "no-ball"
    return "legal"

full["ball_type"] = full.apply(ball_type, axis=1)

# -------------------------------------------------------------------
# Not out flag
# -------------------------------------------------------------------
full["is_not_out"] = full["player_out"].isna().astype(int)

# -------------------------------------------------------------------
# Create opponent team
# -------------------------------------------------------------------
def get_opponent(row):
    bat = row["batting_team"]
    t1 = row["team1"]
    t2 = row["team2"]
    if pd.isna(t1) or pd.isna(t2):
        return None
    return t2 if bat == t1 else t1

full["opponent_team"] = full.apply(get_opponent, axis=1)

# -------------------------------------------------------------------
# Required columns for Table-2
# -------------------------------------------------------------------
wanted = [
    "match_id", "date", "venue", "city", "country",
    "batting_team", "opponent_team",
    "innings_number", "over",
    "batter", "non_striker", "bowler",
    "runs_batter", "runs_extras", "runs_total",
    "four", "six",
    "wicket_kind", "fielder", "player_out",
    "is_not_out", "ball_type",
    "winner"
]

final_cols = [c for c in wanted if c in full.columns]
final = full[final_cols]

# -------------------------------------------------------------------
# Save
# -------------------------------------------------------------------
final.to_csv(out_file, index=False)

print("\n🎉 Table-2 (Filtered to Table-1 Players Only) Saved →", out_file)
print("📦 Total rows:", len(final))
