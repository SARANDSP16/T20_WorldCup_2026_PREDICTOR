import pandas as pd

# ----------------------------
# Paths
# ----------------------------
input_path = r"D:\project\Data_collection_t20\outputs\teams_players.csv"
output_path = r"D:\project\Data_collection_t20\outputs\filtered_team_players.csv"

# ----------------------------
# Load CSV
# ----------------------------
df = pd.read_csv(input_path)
df["team_name"] = df["team_name"].astype(str).str.strip()
df["player_name"] = df["player_name"].astype(str).str.strip()

# ----------------------------
# Required Teams
# ----------------------------
required_teams = [
    "Australia", "Bangladesh", "Canada", "England", "India", "Ireland",
    "Namibia", "Nepal", "Netherlands", "New Zealand", "Oman", "Pakistan",
    "Papua New Guinea", "Scotland", "South Africa", "Sri Lanka", "Uganda",
    "United States of America", "West Indies", "Zimbabwe"
]

# ----------------------------
# Filter dataset
# ----------------------------
filtered_df = df[df["team_name"].isin(required_teams)]

# Remove duplicates
filtered_df = filtered_df.drop_duplicates(subset=["team_name", "player_name"])

# Sort
filtered_df = filtered_df.sort_values(["team_name", "player_name"])

# ----------------------------
# Save Output
# ----------------------------
filtered_df.to_csv(output_path, index=False)

print("✅ Filtered team players saved successfully!")
print(f"📄 Output → {output_path}")
print(f"🧮 Total Teams: {filtered_df['team_name'].nunique()}")
print(f"👥 Total Players: {len(filtered_df)}")
