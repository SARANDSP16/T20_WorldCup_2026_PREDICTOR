import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

table2_path = BASE / "processed" / "table2_match_by_match.csv"
table1_path = BASE / "processed" / "table1_player_career.csv"
out_path = BASE / "processed" / "table7_player_form.csv"

print("📂 Loading Table-2:", table2_path)
df = pd.read_csv(table2_path)

print("📂 Loading Table-1:", table1_path)
players = pd.read_csv(table1_path)

valid = set(players["player_full_name"].astype(str).str.strip())

# Clean names
for col in ["batter", "bowler", "player_out"]:
    df[col] = df[col].astype(str).str.strip()

# Only relevant deliveries
df = df[
    df["batter"].isin(valid) |
    df["bowler"].isin(valid)
].reset_index(drop=True)


# ---------------------------------------------------------
# MATCH-WISE BATTING AGGREGATES
# ---------------------------------------------------------
bat = (
    df.groupby(["match_id", "date", "batter", "batting_team", "opponent_team"], as_index=False)
      .agg(
          runs=("runs_batter", "sum"),
          balls=("runs_batter", "count"),
          fours=("four", "sum"),
          sixes=("six", "sum"),
          dismissals=("player_out", lambda x: x.notna().sum())
      )
)

bat["strike_rate"] = ((bat["runs"] / bat["balls"]) * 100).round(2)
bat.rename(columns={"batter": "player_name", "batting_team": "team"}, inplace=True)


# ---------------------------------------------------------
# MATCH-WISE BOWLING AGGREGATES
# ---------------------------------------------------------
bowl = (
    df.groupby(["match_id", "date", "bowler", "batting_team"], as_index=False)
      .agg(
          balls_bowled=("runs_total", "count"),
          runs_conceded=("runs_total", "sum"),
          wickets=("player_out", lambda x: x.notna().sum())
      )
)

bowl["economy"] = (bowl["runs_conceded"] / (bowl["balls_bowled"] / 6)).round(2)
bowl.rename(columns={"bowler": "player_name", "batting_team": "opponent_team"}, inplace=True)


# ---------------------------------------------------------
# COMBINE BATTING + BOWLING
# ---------------------------------------------------------
combined = pd.merge(
    bat,
    bowl,
    on=["match_id", "date", "player_name", "opponent_team"],
    how="outer"
).fillna(0)

combined["team"] = combined["team"].replace(0, "Unknown")


# ---------------------------------------------------------
# SORT for rolling form
# ---------------------------------------------------------
combined["date"] = pd.to_datetime(combined["date"])
combined = combined.sort_values(["player_name", "date"])


# ---------------------------------------------------------
# ROLLING FORM (Last 5 matches)
# ---------------------------------------------------------
combined["form_batting_5"] = combined.groupby("player_name")["runs"].rolling(5).mean().reset_index(level=0, drop=True).round(2)
combined["form_bowling_5"] = combined.groupby("player_name")["wickets"].rolling(5).mean().reset_index(level=0, drop=True).round(2)


# ---------------------------------------------------------
# Combined Form Index
# ---------------------------------------------------------
combined["rolling_index"] = (
    combined["form_batting_5"] * 0.6 +
    combined["form_bowling_5"] * 4
).round(2)


# ---------------------------------------------------------
# Fantasy Points (Optional)
# ---------------------------------------------------------
combined["fantasy_points"] = (
    combined["runs"] +
    combined["wickets"] * 25 +
    combined["fours"] * 1 +
    combined["sixes"] * 2
).round(2)


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
combined.to_csv(out_path, index=False)
print("\n🎉 Table-7 Player Form Saved →", out_path)
print("📦 Total rows:", len(combined))
