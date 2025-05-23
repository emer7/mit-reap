import csv
from rapidfuzz import fuzz

INPUT_CSV = "Summary Sheets - RegisterPro.csv"
OUTPUT_CSV = "Grouped_Participants.csv"

# The column name for school/major (as in the CSV header)
SCHOOL_MAJOR_COL = "Nama Sekolah/Kampus \r\n(beserta Jurusan khusus untuk Kampus)"

# Read all rows and collect school/major values
rows = []
school_major_list = []
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
        # Normalize to lowercase for grouping
        school_major = row[SCHOOL_MAJOR_COL].strip().lower()
        school_major_list.append(school_major)

# Cluster similar school/major strings using fuzzy matching (case-insensitive)
clusters = []
cluster_map = {}
THRESHOLD = 90  # Adjust as needed for strictness

for value in school_major_list:
    found = False
    for cidx, cluster in enumerate(clusters):
        # Compare with the first value in the cluster
        if fuzz.token_sort_ratio(value, cluster[0]) >= THRESHOLD:
            clusters[cidx].append(value)
            cluster_map[value] = cidx
            found = True
            break
    if not found:
        clusters.append([value])
        cluster_map[value] = len(clusters) - 1

# Assign group id and group name to each row
for row in rows:
    school_major = row[SCHOOL_MAJOR_COL].strip().lower()
    group_id = cluster_map[school_major]
    row["GroupID"] = group_id
    # Use the first value in the cluster as the group name (capitalize for output)
    row["GroupName"] = clusters[group_id][0].title()

# Write to new CSV
fieldnames = list(rows[0].keys())
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Grouped participants written to {OUTPUT_CSV}")
