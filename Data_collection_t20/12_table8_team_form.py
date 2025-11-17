import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

table2_path = BASE / "processed" / "table2_match_by_match.csv"
matches_path = BASE / "outputs" / "matches.csv"
out_path = BASE / "processed" / "table8_team_form.csv"

print("📂 Loading Table-2:", table2_path)
df = pd.read_csv(table2_path)

print("📂 Loading matches:", matches_path)
matches = pd.read_csv(matches_path)

# ---------------------------------------------------------
# BASIC PREP
# ---------------------------------------------------------
df["date"] = pd.to_datetime(df["date"])
matches["date"] = pd.to_datetime(matches["date"])

# Determine team runs per innings
team_runs = (
    df.groupby(["match_id", "batting_team"], as_index=False)
      .agg(
          total_runs=("runs_total", "sum"),
          wickets_lost=("player_out", lambda x: x.notna().sum()),
          balls=("runs_total", "count"),
          fours=("four", "sum"),
          sixes=("six", "sum")
      )
)

team_runs["run_rate"] = (team_runs["total_runs"] / (team_runs["balls"] / 6)).round(2)

# Bowling side (opponent)
bowling_runs = (
    df.groupby(["match_id", "opponent_team"], as_index=False)
      .agg(
          runs_conceded=("runs_total", "sum"),
          wickets_taken=("player_out", lambda x: x.notna().sum()),
          balls=("runs_total", "count")
      )
)
bowling_runs.rename(columns={"opponent_team": "team"}, inplace=True)
team_runs.rename(columns={"batting_team": "team"}, inplace=True)

# Merge batting + bowling
team_combined = team_runs.merge(
    bowling_runs,
    on=["match_id", "team"],
    how="outer"
)

# ---------------------------------------------------------
# ADD MATCH RESULT INFO
# ---------------------------------------------------------
matches_small = matches[["match_id", "team1", "team2", "winner", "result"]]

team_combined = team_combined.merge(matches_small, on="match_id", how="left")

team_combined["won"] = (team_combined["team"] == team_combined["winner"]).astype(int)

# Opponent identification
team_combined["opponent"] = team_combined.apply(
    lambda r: r["team2"] if r["team"] == r["team1"] else r["team1"],
    axis=1
)

# ---------------------------------------------------------
# ROLLING FORM (last 5 matches)
# ---------------------------------------------------------
team_combined = team_combined.sort_values(["team", "match_id"])

team_combined["form_runs"] = (
    team_combined.groupby("team")["total_runs"]
    .rolling(5).mean().reset_index(level=0, drop=True).round(2)
)

team_combined["form_wickets"] = (
    team_combined.groupby("team")["wickets_taken"]
    .rolling(5).mean().reset_index(level=0, drop=True).round(2)
)

team_combined["win_ratio_5"] = (
    team_combined.groupby("team")["won"]
    .rolling(5).mean().reset_index(level=0, drop=True).round(2)
)

# ---------------------------------------------------------
# HEAD-TO-HEAD WIN RATE
# ---------------------------------------------------------
h2h = {}

for _, r in team_combined.iterrows():
    key = tuple(sorted([r.team, r.opponent]))
    if key not in h2h:
        h2h[key] = {"matches": 0, "wins_team1": 0, "wins_team2": 0}
    h2h[key]["matches"] += 1
    if r.team == key[0] and r.won == 1:
        h2h[key]["wins_team1"] += 1
    if r.team == key[1] and r.won == 1:
        h2h[key]["wins_team2"] += 1

def compute_h2h(row):
    key = tuple(sorted([row.team, row.opponent]))
    rec = h2h[key]
    if row.team == key[0]:
        return rec["wins_team1"] / rec["matches"]
    else:
        return rec["wins_team2"] / rec["matches"]

team_combined["h2h_winrate"] = team_combined.apply(compute_h2h, axis=1).round(2)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
team_combined.to_csv(out_path, index=False)

print("\n🎉 Table-8 Team Form Saved →", out_path)
print("📦 Total rows:", len(team_combined))
