import json
import pandas as pd

# ==========================================================
# Step 1: Load JSON and CSV Files
# ==========================================================
players_json_path = r"D:\project\Data_collection_t20\players.json"
team_counts_path = r"D:\project\Data_collection_t20\outputs\team_player_counts.csv"

# Load files
with open(players_json_path, "r", encoding="utf-8") as f:
    players_data = json.load(f)

df_counts = pd.read_csv(team_counts_path)

# Clean team names
df_counts["team_name"] = df_counts["team_name"].astype(str).str.strip()
json_teams = list(players_data.get("teams", {}).keys())
csv_teams = df_counts["team_name"].unique().tolist()

# ==========================================================
# Step 2: Compare Teams
# ==========================================================
common_teams = sorted(set(json_teams) & set(csv_teams))
missing_in_json = sorted(set(csv_teams) - set(json_teams))
missing_in_csv = sorted(set(json_teams) - set(csv_teams))

print("✅ Common Teams Found in Both:")
print(common_teams)

print("\n⚠️ Teams Present in CSV but Missing in JSON:")
print(missing_in_json)

print("\n❌ Teams Present in JSON but Missing in CSV (will be removed):")
print(missing_in_csv)

# ==========================================================
# Step 3: Remove Teams Not Present in CSV
# ==========================================================
cleaned_data = {"teams": {team: players_data["teams"][team] for team in common_teams}}

# Save updated JSON
with open(players_json_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("\n💾 Cleaned players.json saved successfully!")
print(f"✅ Remaining Teams Count: {len(cleaned_data['teams'])}")
print(f"Teams: {', '.join(common_teams)}")
