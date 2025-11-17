import pandas as pd
import os
from pathlib import Path
import json

BASE = Path("D:/project/Data_collection_t20")

deliveries_path = BASE / "outputs" / "deliveries.csv"
mapping_path = BASE / "master_player_match_report.csv"
processed_dir = BASE / "processed"
processed_dir.mkdir(exist_ok=True)

out_file = processed_dir / "table1_player_career.csv"

print("📂 Loading deliveries:", deliveries_path)
df = pd.read_csv(deliveries_path)

print("📂 Loading player mapping:", mapping_path)
map_df = pd.read_csv(mapping_path)

# ---------------------------------------------------------
# Clean player name fields
# ---------------------------------------------------------
for col in ["batter", "bowler", "non_striker", "fielder", "player_out"]:
    df[col] = df[col].astype(str).str.strip()

map_df["player_short_name"] = map_df["player_short_name"].astype(str).str.strip()

# ---------------------------------------------------------
# Filter deliveries to ONLY the 385 mapped players
# ---------------------------------------------------------
valid_players = set(map_df["player_short_name"])

df = df[
    df["batter"].isin(valid_players)
    | df["bowler"].isin(valid_players)
    | df["fielder"].isin(valid_players)
    | df["player_out"].isin(valid_players)
]

print("✅ Deliveries after filtering:", len(df))

# ---------------------------------------------------------
# Batting Stats
# ---------------------------------------------------------
bat = (
    df.groupby("batter", as_index=False)
      .agg(
          matches_played=("match_id", "nunique"),
          innings_batted=("innings_number", "nunique"),
          runs=("runs_batter", "sum"),
          balls_faced=("over", "count"),
          fours=("runs_batter", lambda x: (x == 4).sum()),
          sixes=("runs_batter", lambda x: (x == 6).sum())
      )
)

# Highest score
high = (
    df.groupby(["batter", "match_id"])["runs_batter"]
      .sum()
      .reset_index()
      .groupby("batter")["runs_batter"]
      .max()
      .reset_index()
      .rename(columns={"runs_batter": "highest_score"})
)

bat = bat.merge(high, on="batter", how="left")

bat["fifties"] = (bat["highest_score"].between(50, 99)).astype(int)
bat["hundreds"] = (bat["highest_score"] >= 100).astype(int)

bat["strike_rate"] = (bat["runs"] / bat["balls_faced"] * 100).round(2)

bat["batting_average"] = (
    bat["runs"] / bat["innings_batted"]
).replace([0, float("inf")], None).round(2)

# ---------------------------------------------------------
# Bowling Stats
# ---------------------------------------------------------
bowl = (
    df.groupby("bowler", as_index=False)
      .agg(
          balls_bowled=("over", "count"),
          runs_conceded=("runs_total", "sum"),
          wickets=("player_out", lambda x: x.notna().sum())
      )
)

bowl["bowling_average"] = (
    bowl["runs_conceded"] / bowl["wickets"]
).replace([0, float("inf")], None).round(2)

bowl["economy"] = (bowl["runs_conceded"] / (bowl["balls_bowled"] / 6)).round(2)

# 5 wicket hauls
five = (
    df[df["player_out"].notna()]
    .groupby(["bowler", "match_id"])
    .size()
    .reset_index(name="wkts_in_match")
)

five = (
    five.groupby("bowler")["wkts_in_match"]
        .apply(lambda x: (x >= 5).sum())
        .reset_index()
        .rename(columns={"wkts_in_match": "five_wicket_hauls"})
)

bowl = bowl.merge(five, on="bowler", how="left")
bowl["five_wicket_hauls"] = bowl["five_wicket_hauls"].fillna(0).astype(int)

# ---------------------------------------------------------
# Fielding Stats
# ---------------------------------------------------------
field = (
    df[df["fielder"].notna()]
    .groupby("fielder", as_index=False)
    .agg(
        catches=("wicket_kind", lambda x: (x == "caught").sum()),
        stumpings=("wicket_kind", lambda x: (x == "stumped").sum()),
        run_outs=("wicket_kind", lambda x: (x == "run out").sum())
    )
)

# ---------------------------------------------------------
# Dismissal Breakdown
# ---------------------------------------------------------
dismiss = (
    df[df["player_out"].notna()]
    .groupby(["player_out", "wicket_kind"])
    .size()
    .reset_index(name="count")
)

dismiss_dict = {
    p: grp.set_index("wicket_kind")["count"].to_dict()
    for p, grp in dismiss.groupby("player_out")
}

# ---------------------------------------------------------
# Merge ALL Stats
# ---------------------------------------------------------
career = (
    bat.merge(bowl, left_on="batter", right_on="bowler", how="outer")
       .merge(field, left_on="batter", right_on="fielder", how="outer")
)

career = career.fillna(0)

# ---------------------------------------------------------
# Attach full name + team using mapping file (385 players)
# ---------------------------------------------------------
career = career.merge(
    map_df,
    left_on="batter",
    right_on="player_short_name",
    how="inner"          # ⭐ important — keeps ONLY mapped players
)

# ---------------------------------------------------------
# Add dismissal breakdown
# ---------------------------------------------------------
career["dismissal_breakdown"] = career["batter"].apply(
    lambda x: dismiss_dict.get(x, {})
)

# ---------------------------------------------------------
# Role detection
# ---------------------------------------------------------
def detect_role(row):
    if row["wickets"] > 10 and row["runs"] > 500:
        return "All-rounder"
    if row["wickets"] > 10:
        return "Bowler"
    return "Batter"

career["role"] = career.apply(detect_role, axis=1)

# ---------------------------------------------------------
# Final output formatting
# ---------------------------------------------------------
career["id"] = range(1, len(career) + 1)

final_cols = [
    "id", "player_full_name", "team", "role",
    "matches_played", "innings_batted",
    "runs", "balls_faced", "batting_average", "strike_rate",
    "fifties", "hundreds", "fours", "sixes", "highest_score",
    "wickets", "balls_bowled", "runs_conceded",
    "bowling_average", "economy", "five_wicket_hauls",
    "catches", "stumpings", "run_outs",
    "dismissal_breakdown"
]

final = career[final_cols]

# ---------------------------------------------------------
# Save Table-1
# ---------------------------------------------------------
final.to_csv(out_file, index=False)

print("\n🎉 DONE — Table-1 Player Career Saved:", out_file)
print("Total players:", len(final))
