#!/usr/bin/env python3
"""
0_data_extraction_pipeline.py

Complete pipeline:
  1️⃣ Extract match, deliveries, and team-player data from Cricsheet JSON files.
  2️⃣ Verify presence of 20 target teams.
  3️⃣ Display player counts per team and top players.

Outputs:
 - deliveries.csv
 - matches.csv
 - teams_players.csv
 - team_player_counts.csv

Usage:
    python 0_data_extraction_pipeline.py --input-dir "D:\\project\\Data_collection_t20\\data\\t20s_male_json" --out-dir "D:\\project\\Data_collection_t20\\outputs"
"""

import os
import json
import argparse
from glob import glob
from tqdm import tqdm
import pandas as pd

# ----------------- Helpers ----------------- #
def safe_get(d, *keys, default=None):
    cur = d
    try:
        for k in keys:
            cur = cur[k]
        return cur
    except Exception:
        return default


def parse_match_file(fp):
    """Parse one JSON file and return match meta, deliveries, and team-player mapping."""
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info", {})
    filename = os.path.basename(fp)
    match_id = os.path.splitext(filename)[0]

    # --- Match Meta --- #
    meta = {
        "match_id": match_id,
        "match_type": info.get("match_type"),
        "season": info.get("season"),
        "date": info.get("dates", [None])[0] if isinstance(info.get("dates"), list) else info.get("dates"),
        "venue": info.get("venue"),
        "city": info.get("city"),
        "country": info.get("country"),
        "teams": ",".join(info.get("teams", [])),
        "team1": info.get("teams", [None, None])[0],
        "team2": info.get("teams", [None, None])[1] if len(info.get("teams", [])) > 1 else None,
        "toss_winner": safe_get(info, "toss", "winner"),
        "toss_decision": safe_get(info, "toss", "decision"),
        "winner": safe_get(info, "outcome", "winner"),
        "result": json.dumps(safe_get(info, "outcome", "by")),
        "player_of_match": ",".join(info.get("player_of_match", [])) if info.get("player_of_match") else None,
        "balls_per_over": info.get("balls_per_over"),
        "team_type": info.get("team_type"),
        "gender": info.get("gender"),
    }

    # --- Deliveries --- #
    deliveries_rows = []
    for inn_idx, inn in enumerate(data.get("innings", []), start=1):
        batting_team = inn.get("team")
        for over_entry in inn.get("overs", []):
            over = over_entry.get("over")
            for delivery in over_entry.get("deliveries", []):
                runs = delivery.get("runs", {})
                extras = delivery.get("extras", {})
                wicket_info = delivery.get("wickets", [])
                wicket_kind, player_out, fielders = None, None, None
                if isinstance(wicket_info, list) and wicket_info:
                    w = wicket_info[0]
                    wicket_kind = w.get("kind")
                    player_out = w.get("player_out")
                    if isinstance(w.get("fielders"), list):
                        fielders = ", ".join(
                            [f.get("name") for f in w.get("fielders") if isinstance(f, dict) and f.get("name")]
                        )

                deliveries_rows.append({
                    "match_id": match_id,
                    "innings_number": inn_idx,
                    "batting_team": batting_team,
                    "over": over,
                    "batter": delivery.get("batter"),
                    "non_striker": delivery.get("non_striker"),
                    "bowler": delivery.get("bowler"),
                    "runs_batter": runs.get("batter", 0),
                    "runs_extras": runs.get("extras", 0),
                    "runs_total": runs.get("total", 0),
                    "bye": extras.get("byes"),
                    "legbye": extras.get("legbyes"),
                    "wide": extras.get("wides"),
                    "noball": extras.get("noballs"),
                    "wicket_kind": wicket_kind,
                    "player_out": player_out,
                    "fielder": fielders,
                })

    # --- Team-Player Mapping --- #
    teams_players = []
    players_dict = info.get("players", {})
    for team, players in players_dict.items():
        for player in players:
            teams_players.append({
                "match_id": match_id,
                "team_name": team,
                "player_name": player
            })

    return meta, deliveries_rows, teams_players


# ----------------- Main ----------------- #
def main(input_dir, out_dir, overwrite=False):
    os.makedirs(out_dir, exist_ok=True)

    deliveries_out = os.path.join(out_dir, "deliveries.csv")
    matches_out = os.path.join(out_dir, "matches.csv")
    team_players_out = os.path.join(out_dir, "teams_players.csv")
    team_player_counts_out = os.path.join(out_dir, "team_player_counts.csv")

    pattern = os.path.join(input_dir, "**", "*.json")
    files = sorted(glob(pattern, recursive=True))
    if not files:
        print(f"❌ No JSON files found in {input_dir}")
        return

    print(f"📂 Found {len(files)} JSON match files")

    matches, deliveries, team_players = [], [], []

    for fp in tqdm(files, desc="Parsing matches"):
        try:
            meta, del_rows, tp_rows = parse_match_file(fp)
            matches.append(meta)
            deliveries.extend(del_rows)
            team_players.extend(tp_rows)
        except Exception as e:
            print(f"⚠️ Error parsing {fp}: {e}")

    # Save extracted data
    pd.DataFrame(matches).to_csv(matches_out, index=False, encoding="utf-8")
    pd.DataFrame(deliveries).to_csv(deliveries_out, index=False, encoding="utf-8")
    df_teams = pd.DataFrame(team_players)
    df_teams.to_csv(team_players_out, index=False, encoding="utf-8")

    print("\n✅ Data Extraction Complete!")
    print(f"💾 Matches -> {matches_out}")
    print(f"💾 Deliveries -> {deliveries_out}")
    print(f"💾 Teams & Players -> {team_players_out}")

    # ---------------------------------------------------------------------- #
    # 🔍 Post Extraction Verification
    # ---------------------------------------------------------------------- #
    print("\n🔎 Running Team & Player Verification...")

    # Clean and check data
    df_teams["team_name"] = df_teams["team_name"].astype(str).str.strip()
    df_teams["player_name"] = df_teams["player_name"].astype(str).str.strip()

    target_teams = [
        "India", "Sri Lanka", "Afghanistan", "Australia", "Bangladesh", "England",
        "South Africa", "USA", "West Indies", "Ireland", "New Zealand", "Pakistan",
        "Canada", "Italy", "Netherlands", "Namibia", "Zimbabwe", "Nepal", "Oman", "UAE"
    ]

    existing_teams = df_teams["team_name"].unique().tolist()
    found = sorted(set(existing_teams) & set(target_teams))
    missing = sorted(set(target_teams) - set(existing_teams))

    print("\n✅ Teams Found:\n", found)
    print("\n❌ Missing Teams:\n", missing)

    # Player count per team
    team_counts = (
        df_teams.groupby("team_name")["player_name"]
        .nunique()
        .reset_index(name="player_count")
        .sort_values(by="player_count", ascending=False)
    )

    print("\n📊 Player Count per Team:")
    print(team_counts.to_string(index=False))

    # Save player count summary
    team_counts.to_csv(team_player_counts_out, index=False, encoding="utf-8")
    print(f"\n💾 Saved player count summary -> {team_player_counts_out}")

    # Example player display
    example_teams = ["India", "Australia", "England"]
    for team in example_teams:
        if team in df_teams["team_name"].values:
            players = df_teams[df_teams["team_name"] == team]["player_name"].unique().tolist()
            print(f"\n🏏 {team} ({len(players)} Players):")
            print(players[:20])
        else:
            print(f"\n⚠️ {team} not found in dataset.")

    # Final summary
    print("\n📈 Summary Stats:")
    print(f"Total Matches: {len(matches)}")
    print(f"Total Deliveries: {len(deliveries)}")
    print(f"Unique Teams: {df_teams['team_name'].nunique()}")
    print(f"Unique Players: {df_teams['player_name'].nunique()}")


# ----------------- CLI ----------------- #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Path to Cricsheet JSON folder")
    parser.add_argument("--out-dir", default="outputs", help="Output folder")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite old CSV files")
    args = parser.parse_args()

    main(args.input_dir, args.out_dir, overwrite=args.overwrite)
