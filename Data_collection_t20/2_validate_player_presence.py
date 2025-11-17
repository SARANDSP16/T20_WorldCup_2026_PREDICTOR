import pandas as pd
import json
from rapidfuzz import process, fuzz
from pathlib import Path
import os

# ----------------------------
# Paths
# ----------------------------
BASE = Path("D:/project/Data_collection_t20")
deliveries_path = BASE / "outputs" / "deliveries.csv"
players_json = BASE / "players.json"
json_dir = BASE / "data" / "t20s_male_json"
out_path = BASE / "outputs" / "player_match_names.csv"

print(f"📂 Reading deliveries file: {deliveries_path}")
df = pd.read_csv(deliveries_path)
print(f"✅ Columns: {list(df.columns)}")

# ----------------------------
# Load player list
# ----------------------------
print(f"📂 Loading players.json: {players_json}")
with open(players_json, "r", encoding="utf-8") as f:
    data = json.load(f)
teams_data = data.get("teams", {})
all_team_players = [p for team in teams_data.values() for p in team]

# ----------------------------
# Helper: fuzzy match
# ----------------------------
def best_match(name, choices, threshold=80):
    """Find best fuzzy match with token sort ratio."""
    match = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        return match[0], match[1]
    return None, 0

# ----------------------------
# Batting stats
# ----------------------------
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
bat["strike_rate"] = (bat["runs"] / bat["balls_faced"] * 100).round(2)

# Highest score
high = df.groupby(["batter", "match_id"])["runs_batter"].sum().reset_index()
high = (
    high.groupby("batter")["runs_batter"]
    .max()
    .reset_index()
    .rename(columns={"runs_batter": "highest_score"})
)
bat = bat.merge(high, on="batter", how="left")

bat["fifties"] = (bat["highest_score"].between(50, 99)).astype(int)
bat["hundreds"] = (bat["highest_score"] >= 100).astype(int)

# ----------------------------
# Bowling stats
# ----------------------------
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
).replace([float("inf"), 0], None).round(2)
bowl["economy"] = (bowl["runs_conceded"] / (bowl["balls_bowled"] / 6)).round(2)

# ----------------------------
# Fielding stats
# ----------------------------
field = (
    df[df["fielder"].notna()]
    .groupby("fielder", as_index=False)
    .agg(
        catches=("wicket_kind", lambda x: (x == "caught").sum()),
        stumpings=("wicket_kind", lambda x: (x == "stumped").sum()),
        run_outs=("wicket_kind", lambda x: (x == "run out").sum())
    )
)

# ----------------------------
# Merge all stats
# ----------------------------
career = (
    bat.merge(bowl, left_on="batter", right_on="bowler", how="outer")
    .merge(field, left_on="batter", right_on="fielder", how="outer")
)
career = career.fillna(0)

# ----------------------------
# Fuzzy match full player names
# ----------------------------
all_names = (
    career["batter"]
    .dropna()
    .astype(str)
    .apply(lambda x: x.strip())
    .unique()
    .tolist()
)

fuzzy_map = []
unmatched_players = []

print(f"🧩 Matching {len(all_team_players)} known players across {len(teams_data)} teams...")

for team, players in teams_data.items():
    for player in players:
        if not isinstance(player, str) or player.strip() == "":
            continue
        best, score = best_match(player, all_names, threshold=75)
        if best:
            fuzzy_map.append({
                "team": team,
                "full_name": player,
                "matched_in_data": best,
                "confidence": score
            })
        else:
            unmatched_players.append({"team": team, "player": player})

fuzzy_df = pd.DataFrame(fuzzy_map)
print(f"✅ Matched {len(fuzzy_df)} players with confidence ≥75%")

# ----------------------------
# Combine fuzzy names with stats
# ----------------------------
career = career.merge(fuzzy_df, left_on="batter", right_on="matched_in_data", how="inner")

career["role"] = career.apply(
    lambda x: "All-rounder"
    if (x["wickets"] > 10 and x["runs"] > 500)
    else "Bowler" if x["wickets"] > 10
    else "Batter",
    axis=1
)

career["batting_average"] = (
    career["runs"] / career["innings_batted"]
).replace([float("inf"), 0], None).round(2)

final_cols = [
    "full_name", "team", "role", "matches_played", "innings_batted",
    "runs", "balls_faced", "batting_average", "strike_rate",
    "fifties", "hundreds", "fours", "sixes", "highest_score",
    "wickets", "balls_bowled", "runs_conceded", "bowling_average",
    "economy", "catches", "stumpings", "run_outs", "confidence"
]

final_df = career[final_cols].sort_values(by="runs", ascending=False)
final_df.to_csv(out_path, index=False)

print(f"\n🏏 Table-1 Saved → {out_path}")
print(f"Total Players: {len(final_df)}")

# ----------------------------
# TEAM-WISE REPORT FOLDER
# ----------------------------
team_report_folder = BASE / "outputs" / "player_reports"
team_report_folder.mkdir(exist_ok=True)

print("\n📁 Creating team-wise reports...")

for team in teams_data.keys():
    team_file = team_report_folder / f"{team.replace(' ', '_')}.txt"
    lines = []
    lines.append(f"TEAM: {team}")
    lines.append("=" * 50)

    t_matches = fuzzy_df[fuzzy_df["team"] == team]

    if len(t_matches) == 0:
        lines.append("No matched players.")
    else:
        for _, row in t_matches.iterrows():
            lines.append(f"{row['full_name']}  |  {row['matched_in_data']}  |  {row['confidence']}")

    # Unmatched
    um = [u["player"] for u in unmatched_players if u["team"] == team]
    if um:
        lines.append("\nUNMATCHED PLAYERS:")
        lines.append("-" * 30)
        for p in um:
            lines.append(f"- {p}")

    with open(team_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

print("✅ Team-wise reports created!")

# ----------------------------
# MASTER TEXT REPORT
# ----------------------------
text_report_path = BASE / "outputs" / "player_match_report.txt"
lines_master = []

lines_master.append("MASTER PLAYER MATCH REPORT")
lines_master.append("=" * 70 + "\n")

# Matched
lines_master.append("MATCHED PLAYERS\n------------------")
for _, row in fuzzy_df.iterrows():
    lines_master.append(
        f"{row['team']} | {row['full_name']} | {row['matched_in_data']} | {row['confidence']}"
    )

# Unmatched
lines_master.append("\nUNMATCHED PLAYERS\n------------------")
for u in unmatched_players:
    lines_master.append(f"{u['team']} | {u['player']} | NOT MATCHED")

with open(text_report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_master))

print(f"📝 Master text report saved → {text_report_path}")
print("🎉 All tasks complete!")
