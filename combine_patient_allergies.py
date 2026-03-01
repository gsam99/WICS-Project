import pandas as pd

# ── 1. Load CSVs ──────────────────────────────────────────────────────────────
patients_meds_df  = pd.read_csv("/Users/neharani/Documents/University/Hackathon/combined_patients_medications.csv")
allergies_drug_df = pd.read_csv("/Users/neharani/Documents/University/Hackathon/combined_allergies_drugdata.csv")

print(f"📥 Loaded combined_patients_medications.csv : {len(patients_meds_df):,} rows")
print(f"📥 Loaded combined_allergies_drugdata.csv   : {len(allergies_drug_df):,} rows")

# ── 2. Rename columns for clarity before merging ─────────────────────────────
# From allergies+drug file we only need: PATIENT, DrugName, Indication
allergies_drug_slim = allergies_drug_df[["PATIENT", "DrugName", "Indication"]].copy()
allergies_drug_slim.rename(columns={"PATIENT": "patient_id"}, inplace=True)

# ── 3. Normalize drug names for matching (strip whitespace + lowercase) ───────
# drug_name in medications can have extra spaces e.g. "Ibuprofen    [Ibu]"
# so we strip and lowercase both sides for matching
patients_meds_df["_drug_key"]     = patients_meds_df["drug_name"].str.strip().str.lower()
allergies_drug_slim["_drug_key"]  = allergies_drug_slim["DrugName"].str.strip().str.lower()

# Also handle cases like "Ibuprofen    [Ibu]" — extract just the base name before spaces/brackets
patients_meds_df["_drug_key"]    = patients_meds_df["_drug_key"].str.split(r'\s{2,}|\[').str[0].str.strip()
allergies_drug_slim["_drug_key"] = allergies_drug_slim["_drug_key"].str.split(r'\s{2,}|\[').str[0].str.strip()

# ── 4. Deduplicate allergies_drug_slim on (patient_id + drug key) ─────────────
before = len(allergies_drug_slim)
allergies_drug_slim.drop_duplicates(subset=["patient_id", "_drug_key"], keep="first", inplace=True)
print(f"🧹 Allergy/drug duplicates removed : {before - len(allergies_drug_slim)} rows dropped")

# ── 5. Left join on patient_id + normalized drug name ────────────────────────
# Left join keeps all medication rows; Indication will be NaN if no match found
combined_df = patients_meds_df.merge(
    allergies_drug_slim[["patient_id", "_drug_key", "Indication"]],
    on=["patient_id", "_drug_key"],
    how="left"
)

# ── 6. Drop the helper key column ─────────────────────────────────────────────
combined_df.drop(columns=["_drug_key"], inplace=True)

# ── 7. Sort by patient_id and START date ─────────────────────────────────────
combined_df.sort_values(by=["patient_id", "START"], inplace=True)
combined_df.reset_index(drop=True, inplace=True)

# ── 8. Save output ────────────────────────────────────────────────────────────
output_path = "combined_patients_medications_with_indication.csv"
combined_df.to_csv(output_path, index=False)

print(f"\n✅ Done! Output saved to : {output_path}")
print(f"   Final rows : {len(combined_df):,}")
print(f"   Columns    : {list(combined_df.columns)}")

# ── 9. Quick summary: how many rows got an Indication matched ─────────────────
matched   = combined_df["Indication"].notna().sum()
unmatched = combined_df["Indication"].isna().sum()
print(f"\n📊 Indication matched   : {matched:,} rows")
print(f"   Indication unmatched : {unmatched:,} rows (drug not in allergy/drug file)")
print()
print(combined_df[["patient_id", "drug_name", "Indication"]].head(10).to_string(index=False))