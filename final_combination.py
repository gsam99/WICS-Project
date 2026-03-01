import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             ConfusionMatrixDisplay, roc_auc_score)
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ═══════════════════════════════════════════════════════════════════
df = pd.read_csv("/Users/neharani/Documents/University/Hackathon/combined_disease_drug_patient.csv")
print(f"📥 Loaded : {len(df):,} rows  |  {df.shape[1]} columns")

# ═══════════════════════════════════════════════════════════════════
# 2. FILTER — only rows where Indication exists (this is our target)
# ═══════════════════════════════════════════════════════════════════
# TO:
df["Indication"] = df["Indication"].astype(str).str.strip()
df = df[~df["Indication"].isin(["nan", "None", ""])]
print(f"📊 Rows with Indication label : {len(df):,}")
print(f"📊 Unique Indications         : {df['Indication'].nunique()}")
print(df["Indication"].value_counts())

# ═══════════════════════════════════════════════════════════════════
# 3. FEATURE ENGINEERING — CLINICAL FACTORS
# ═══════════════════════════════════════════════════════════════════

# Duration of dosage (days)
df["first_administered"] = pd.to_datetime(df["first_administered"], errors="coerce")
df["last_administered"]  = pd.to_datetime(df["last_administered"],  errors="coerce")
df["duration_days"] = (df["last_administered"] - df["first_administered"]).dt.days.fillna(0)

# Dosage
df["dosage_mg"] = pd.to_numeric(df["dosage_mg"], errors="coerce")
df["dosage_mg"].fillna(df["dosage_mg"].median(), inplace=True)

# Times administered
df["times_administered"] = pd.to_numeric(df["times_administered"], errors="coerce").fillna(1)

# ═══════════════════════════════════════════════════════════════════
# 4. SELECT FEATURES
# ═══════════════════════════════════════════════════════════════════
feature_cols = [
    "AGE",
    "GENDER",
    "ETHNICITY",
    "condition",
    "drug_name",
    "dosage_mg",
    "duration_days",
    "times_administered",
]
feature_cols = [c for c in feature_cols if c in df.columns]

df_model = df[feature_cols + ["Indication"]].dropna()
print(f"\n📊 Model dataset : {len(df_model):,} rows after dropping nulls")

# ═══════════════════════════════════════════════════════════════════
# 5. ENCODE CATEGORICAL FEATURES
# ═══════════════════════════════════════════════════════════════════
cat_cols = [c for c in ["GENDER", "ETHNICITY", "condition", "drug_name"] if c in df_model.columns]

le_dict = {}
for col in cat_cols:
    le = LabelEncoder()
    df_model = df_model.copy()
    df_model[col] = le.fit_transform(df_model[col].astype(str))
    le_dict[col] = le

# Encode target — Indication
df_model["Indication"] = df_model["Indication"].str.strip()
le_target = LabelEncoder()
df_model["indication_encoded"] = le_target.fit_transform(df_model["Indication"])

print(f"\n🏷️  Indication classes ({len(le_target.classes_)}):")
for i, cls in enumerate(le_target.classes_):
    print(f"   {i} → {cls}")

X = df_model[feature_cols]
y = df_model["indication_encoded"]

# ═══════════════════════════════════════════════════════════════════
# 6. TRAIN / TEST SPLIT
# ═══════════════════════════════════════════════════════════════════
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n📊 Train : {len(X_train):,} rows  |  Test : {len(X_test):,} rows")

# ═══════════════════════════════════════════════════════════════════
# 7. TRAIN SVM WITH PROBABILITY CALIBRATION
# probability=True enables predict_proba() so we get % per class
# ═══════════════════════════════════════════════════════════════════
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model",  SVC(
        kernel="rbf",            # RBF kernel handles non-linear relationships
        C=1.0,                   # regularization strength
        gamma="scale",           # auto-scales with number of features
        probability=True,        # CRITICAL: enables probability output per class
        class_weight="balanced", # handles class imbalance
        random_state=42
    ))
])

pipeline.fit(X_train, y_train)
y_pred       = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)

# ═══════════════════════════════════════════════════════════════════
# 8. EVALUATION
# ═══════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("📋 CLASSIFICATION REPORT")
print("="*60)
print(classification_report(y_test, y_pred, target_names=le_target.classes_))

if len(le_target.classes_) > 2:
    roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class="ovr", average="weighted")
    print(f"🎯 Weighted ROC-AUC Score : {roc_auc:.4f}")

# Cross-validation for reliable accuracy estimate
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
print(f"📊 5-Fold Cross-Val Accuracy : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ═══════════════════════════════════════════════════════════════════
# 9. PROBABILITY OUTPUT PER PATIENT
# Each patient gets a % probability for every Indication class
# e.g. "Pain, inflammation: 80%", "Type 2 diabetes: 12%", etc.
# ═══════════════════════════════════════════════════════════════════
prob_cols_names = [
    f"prob_{cls.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '')}"
    for cls in le_target.classes_
]
prob_df = pd.DataFrame(y_pred_proba, columns=prob_cols_names)
prob_df["predicted_indication"] = le_target.inverse_transform(y_pred)
prob_df["actual_indication"]    = le_target.inverse_transform(y_test.values)
prob_df["correct"]              = prob_df["predicted_indication"] == prob_df["actual_indication"]

# Add original features back for context
prob_df = pd.concat([X_test.reset_index(drop=True), prob_df], axis=1)

# Format as percentages for readability
for col in prob_cols_names:
    prob_df[col] = (prob_df[col] * 100).round(2).astype(str) + "%"

print("\n📊 Sample Patient Predictions with Probabilities:")
display_cols = ["predicted_indication", "actual_indication", "correct"] + prob_cols_names
print(prob_df[display_cols].head(10).to_string(index=False))

# ═══════════════════════════════════════════════════════════════════
# 10. PLOTS
# ═══════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Drug Indication Prediction — SVM with Probability Output", fontsize=13)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm, display_labels=le_target.classes_).plot(
    ax=axes[0], colorbar=False, xticks_rotation=45
)
axes[0].set_title("Confusion Matrix")

# Indication class distribution in training set
train_counts = pd.Series(le_target.inverse_transform(y_train)).value_counts().sort_values()
train_counts.plot(kind="barh", ax=axes[1], color="steelblue")
axes[1].set_title("Training Data\nIndication Class Distribution")
axes[1].set_xlabel("Number of samples")

plt.tight_layout()
plt.savefig("svm_indication_results.png", dpi=150, bbox_inches="tight")
print("\n📊 Plot saved to : svm_indication_results.png")

# ═══════════════════════════════════════════════════════════════════
# 11. SAVE PREDICTIONS
# ═══════════════════════════════════════════════════════════════════
prob_df.to_csv("indication_predictions_with_probabilities.csv", index=False)
print("✅ Predictions saved to : indication_predictions_with_probabilities.csv")