import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

table2_path = BASE / "processed" / "table2_match_by_match.csv"
matches_path = BASE / "outputs" / "matches.csv"
table1_path = BASE / "processed" / "table1_player_career.csv"

out_path = BASE / "processed" / "table5_match_summary.csv"

print("📂 Loading Table-2:", table2_path)
df = pd.read_csv(table2_path)

print("📂 Loading Matches:", matches_path)
matches = pd.read_csv(matches_path)

print("📂 Loading Table-1:", table1_path)
table1 = pd.read_csv(table1_path)

valid_players = set(table1["player_full_name"])

# Clean
df["batter"] = df["batter"].astype(str).str.strip()
df["bowler"] = df["bowler"].astype(str).str.strip()
df["player_out"] = df["player_out"].astype(str).str.strip()

# --------------------------------------------------------------------
# 1️⃣ TEAM RUN TOTALS + WICKETS PER MATCH
# --------------------------------------------------------------------
team_runs = (
    df.groupby(["match_id", "batting_team"], as_index=False)
      .agg(
          team_runs=("runs_total", "sum"),
          team_wkts=("player_out", lambda x: x.notna().sum())
      )
)

# Rename for merging match metadata later
team_runs["team_order"] = team_runs.groupby("match_id").cumcount() + 1
team_runs = team_runs.pivot(
    index="match_id",
    columns="team_order",
    values=["batting_team", "team_runs", "team_wkts"]
)

team_runs.columns = [
    f"{col[0]}{col[1]}" for col in team_runs.columns
]

team_runs.reset_index(inplace=True)

# --------------------------------------------------------------------
# 2️⃣ TOP SCORER per match
# --------------------------------------------------------------------
top_scorer = (
    df[df["batter"].isin(valid_players)]
    .groupby(["match_id", "batter"], as_index=False)
    .agg(runs=("runs_batter", "sum"))
)

top_scorer = top_scorer.sort_values(["match_id", "runs"], ascending=[True, False])
top_scorer = top_scorer.groupby("match_id").first().reset_index()
top_scorer.rename(columns={"batter": "top_scorer", "runs": "top_scorer_runs"}, inplace=True)

# --------------------------------------------------------------------
# 3️⃣ TOP BOWLER per match
# --------------------------------------------------------------------
top_bowler = (
    df[df["bowler"].isin(valid_players)]
    .groupby(["match_id", "bowler"], as_index=False)
    .agg(wkts=("player_out", lambda x: x.notna().sum()))
)

top_bowler = top_bowler.sort_values(["match_id", "wkts"], ascending=[True, False])
top_bowler = top_bowler.groupby("match_id").first().reset_index()
top_bowler.rename(columns={"bowler": "top_bowler", "wkts": "top_bowler_wkts"}, inplace=True)

# --------------------------------------------------------------------
# 4️⃣ Merge Match Metadata
# --------------------------------------------------------------------
summary = matches[
    ["match_id", "date", "venue", "city", "country", "team1", "team2", "winner"]
]

# Add team totals
summary = summary.merge(team_runs, on="match_id", how="left")

# Add performer data
summary = summary.merge(top_scorer, on="match_id", how="left")
summary = summary.merge(top_bowler, on="match_id", how="left")

# --------------------------------------------------------------------
# 5️⃣ Calculate victory margins (runs or wickets)
# --------------------------------------------------------------------
def calculate_result(row):
    t1 = row["batting_team1"]
    t2 = row["batting_team2"]

    r1 = row["team_runs1"]
    r2 = row["team_runs2"]

    winner = row["winner"]

    if pd.isna(r1) or pd.isna(r2):
        return pd.Series({"margin_runs": None, "margin_wkts": None})

    if winner == t1:
        return pd.Series({
            "margin_runs": r1 - r2 if r1 > r2 else None,
            "margin_wkts": None
        })
    elif winner == t2:
        return pd.Series({
            "margin_runs": r2 - r1 if r2 > r1 else None,
            "margin_wkts": None
        })
    return pd.Series({"margin_runs": None, "margin_wkts": None})

summary[["margin_runs", "margin_wkts"]] = summary.apply(calculate_result, axis=1)

# --------------------------------------------------------------------
# SAVE
# --------------------------------------------------------------------
summary.to_csv(out_path, index=False)

print("\n🎉 Table-5 Match Summary Saved →", out_path)
print("📦 Rows:", len(summary))
