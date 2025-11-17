import pandas as pd
from pathlib import Path

BASE = Path("D:/project/Data_collection_t20")

t2 = BASE / "processed" / "table2_match_by_match.csv"
t1 = BASE / "processed" / "table1_player_career.csv"
out = BASE / "processed" / "table6_over_and_partnership.csv"

print("📂 Loading Table-2:", t2)
df = pd.read_csv(t2)

print("📂 Loading Table-1:", t1)
players = pd.read_csv(t1)

# ---------------------------------------------------------
# Filter only 385 valid players
# ---------------------------------------------------------
valid = set(players["player_full_name"].astype(str).str.strip())

for col in ["batter", "non_striker", "bowler", "player_out", "fielder"]:
    df[col] = df[col].astype(str).str.strip()

df = df[
    df["batter"].isin(valid)
    | df["non_striker"].isin(valid)
    | df["bowler"].isin(valid)
].reset_index(drop=True)

print("✅ Deliveries kept:", len(df))

# ---------------------------------------------------------
# 1️⃣ Over-wise Aggregates
# ---------------------------------------------------------
over_df = (
    df.groupby(["match_id", "batting_team", "over"], as_index=False)
      .agg(
          runs_in_over=("runs_total", "sum"),
          wickets_in_over=("player_out", lambda x: x.notna().sum()),
          balls_in_over=("match_id", "count")
      )
)

over_df["run_rate"] = (
    over_df["runs_in_over"] / (over_df["balls_in_over"] / 6)
).round(2)

# ---------------------------------------------------------
# 2️⃣ Partnership Calculation (Fix: Reset Index!)
# ---------------------------------------------------------
df = df.reset_index(drop=True)
df["is_wicket"] = df["player_out"].notna().astype(int)

df["partnership_id"] = df.groupby(
    ["match_id", "batting_team"]
)["is_wicket"].cumsum()

# Partnership totals
partner_df = (
    df.groupby(["match_id", "batting_team", "partnership_id"], as_index=False)
      .agg(
          partnership_runs=("runs_total", "sum"),
          balls=("match_id", "count"),
          batters=("batter", lambda x: list(pd.unique(x)))
      )
)

# Clean batter pairs
partner_df["batters"] = partner_df["batters"].apply(
    lambda x: x[:2] if len(x) >= 2 else x + ["NA"]
)

# ---------------------------------------------------------
# 3️⃣ MERGE Over-wise + Partnership
# ---------------------------------------------------------
merged = df[
    ["match_id", "batting_team", "over", "partnership_id"]
].drop_duplicates()

merged = merged.merge(
    over_df,
    left_on=["match_id", "batting_team", "over"],
    right_on=["match_id", "batting_team", "over"],
    how="left"
)

merged = merged.merge(
    partner_df,
    on=["match_id", "batting_team", "partnership_id"],
    how="left"
)

# ---------------------------------------------------------
# 4️⃣ Cumulative Metrics
# ---------------------------------------------------------
merged = merged.sort_values(["match_id", "batting_team", "over"])

merged["cumulative_runs"] = merged.groupby(
    ["match_id", "batting_team"]
)["runs_in_over"].cumsum()

merged["cumulative_balls"] = merged.groupby(
    ["match_id", "batting_team"]
)["balls_in_over"].cumsum()

merged["cumulative_rr"] = (
    merged["cumulative_runs"] / (merged["cumulative_balls"] / 6)
).round(2)

merged["projected_score"] = (merged["cumulative_rr"] * 20).round(0)

# ---------------------------------------------------------
# Final Output
# ---------------------------------------------------------
final_cols = [
    "match_id", "batting_team", "over",
    "runs_in_over", "wickets_in_over", "balls_in_over",
    "run_rate", "cumulative_rr", "projected_score",
    "partnership_id", "batters", "partnership_runs"
]

final = merged[final_cols]

final.to_csv(out, index=False)

print("\n🎉 Table-6 Over + Partnership Saved →", out)
print("📦 Rows:", len(final))
