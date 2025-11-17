import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

table2_path = BASE / "processed" / "table2_match_by_match.csv"
table1_path = BASE / "processed" / "table1_player_career.csv"
out_path = BASE / "processed" / "table4_player_vs_venue.csv"

print("📂 Loading Table-2:", table2_path)
df = pd.read_csv(table2_path)

print("📂 Loading Table-1:", table1_path)
table1 = pd.read_csv(table1_path)

# ---------------------------------------------------------
# VALID PLAYERS = Only 385 players
# ---------------------------------------------------------
valid_players = set(table1["player_full_name"].astype(str).str.strip())

# Clean name fields
for col in ["batter", "bowler", "player_out", "fielder"]:
    df[col] = df[col].astype(str).str.strip()

# ---------------------------------------------------------
# Filter rows involving these players
# ---------------------------------------------------------
df = df[
    df["batter"].isin(valid_players)
    | df["bowler"].isin(valid_players)
    | df["player_out"].isin(valid_players)
]

print("✅ Deliveries kept for Table-4:", len(df))

# Fill missing city/country for export only, not grouping
df["city"] = df["city"].fillna("")
df["country"] = df["country"].fillna("")

# ---------------------------------------------------------
# 1️⃣ BATTING vs VENUE
# ---------------------------------------------------------
bat = (
    df.groupby(["batter", "venue"], as_index=False)
      .agg(
          matches=("match_id", "nunique"),
          runs=("runs_batter", "sum"),
          balls=("runs_batter", "count"),
          fours=("four", "sum"),
          sixes=("six", "sum"),
          dismissals=("player_out", lambda x: x.notna().sum())
      )
)

bat["strike_rate"] = ((bat["runs"] / bat["balls"]) * 100).round(2)
bat["avg"] = (
    bat["runs"] / bat["dismissals"].replace(0, None)
).round(2)

bat.rename(columns={"batter": "player_name"}, inplace=True)

# ---------------------------------------------------------
# 2️⃣ BOWLING vs VENUE
# ---------------------------------------------------------
bowl = (
    df.groupby(["bowler", "venue"], as_index=False)
      .agg(
          matches=("match_id", "nunique"),
          balls=("runs_total", "count"),
          runs_conceded=("runs_total", "sum"),
          wickets=("player_out", lambda x: x.notna().sum()),
      )
)

bowl["economy"] = (bowl["runs_conceded"] / (bowl["balls"] / 6)).round(2)
bowl["bowling_avg"] = (
    bowl["runs_conceded"] / bowl["wickets"].replace(0, None)
).round(2)

bowl.rename(columns={"bowler": "player_name"}, inplace=True)

# ---------------------------------------------------------
# 3️⃣ MERGE batting + bowling
# ---------------------------------------------------------
final = pd.merge(
    bat, bowl,
    on=["player_name", "venue"],
    how="outer"
)

# Attach city/country (optional)
venue_info = df.groupby("venue")[["city", "country"]].first().reset_index()
final = final.merge(venue_info, on="venue", how="left")

# Replace NaN with 0 or empty
final = final.fillna({"runs": 0, "balls": 0, "fours": 0, "sixes": 0,
                      "dismissals": 0, "economy": 0, "bowling_avg": 0})

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
final.to_csv(out_path, index=False)

print("\n🎉 Table-4 Player vs Venue Saved →", out_path)
print("📦 Total rows:", len(final))
