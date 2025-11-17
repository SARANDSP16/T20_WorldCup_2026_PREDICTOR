import pandas as pd
import re

# ----- INPUT & OUTPUT PATHS -----
input_path = r"D:\project\Data_collection_t20\MASTER PLAYER MATCH REPORT.txt"
output_path = r"D:\project\Data_collection_t20\master_player_match_report.csv"

print("📂 Reading:", input_path)

with open(input_path, "r", encoding="utf-8") as f:
    text = f.read()

rows = []

# -------------------------------------------------
# 1) MATCH rows in this format:
#    Australia | Sean Abbott | SA Abbott | 80.0
# -------------------------------------------------
pattern1 = re.compile(r"(.+?) \| (.+?) \| (.+?) \|", re.MULTILINE)

for team, full, short in pattern1.findall(text):
    rows.append([team.strip(), full.strip(), short.strip()])

# -------------------------------------------------
# 2) MATCH rows in this format:
#    India,Sai Kishore,R Sai Kishore
# -------------------------------------------------
pattern2 = re.compile(r"([A-Za-z ]+),([A-Za-z .'-]+),([A-Za-z .'-]+)")

for team, full, short in pattern2.findall(text):
    rows.append([team.strip(), full.strip(), short.strip()])

# -------------------------------------------------
#  Save final CSV
# -------------------------------------------------
df = pd.DataFrame(rows, columns=["team", "player_full_name", "player_short_name"])
df = df.drop_duplicates()

df.to_csv(output_path, index=False, encoding="utf-8")

print("✅ CSV Saved Successfully!")
print("➡", output_path)
print("Total rows:", len(df))
