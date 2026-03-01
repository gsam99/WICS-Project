import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc

# ----------------------------
# 1. Load Data
# ----------------------------
df = pd.read_csv("/Users/neharani/Documents/University/Hackathon/combined_disease_drug_patient.csv")

# ----------------------------
# 2. Clean Dates
# ----------------------------
df['first_administered'] = pd.to_datetime(df['first_administered'], errors='coerce')
df['last_administered'] = pd.to_datetime(df['last_administered'], errors='coerce')
df['last_administered'] = df['last_administered'].fillna(df['first_administered'])

df['treatment_duration_days'] = (df['last_administered'] - df['first_administered']).dt.days
df['treatment_duration_days'] = df['treatment_duration_days'].clip(lower=0).fillna(0)

# ----------------------------
# 3. Clean Numeric Columns
# ----------------------------
numeric_cols = ['dosage_mg','times_administered','total_cost']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ----------------------------
# 4. Aggregate per Patient + Drug
# ----------------------------
df_model = df.groupby(['patient_id','drug_name']).agg({
    'AGE':'first',
    'GENDER':'first',
    'ETHNICITY':'first',
    'dosage_mg':'mean',
    'times_administered':'sum',
    'treatment_duration_days':'mean',
    'INCOME':'first',
    'HEALTHCARE_EXPENSES':'first',
    'HEALTHCARE_COVERAGE':'first',
    'total_cost':'sum'
}).reset_index()

# ----------------------------
# 5. Encode Categoricals
# ----------------------------
cat_cols = ['GENDER','ETHNICITY','drug_name']
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df_model[col] = le.fit_transform(df_model[col].astype(str))
    encoders[col] = le  # save encoder for later

# ----------------------------
# 6. Define Severity Levels
# ----------------------------
def assign_severity(row):
    score = row['dosage_mg'] + row['times_administered'] + row['treatment_duration_days']
    if score < 5:
        return "low"
    elif score < 50:
        return "medium"
    else:
        return "high"

df_model['severity'] = df_model.apply(assign_severity, axis=1)

# Encode severity
severity_encoder = LabelEncoder()
df_model['severity_encoded'] = severity_encoder.fit_transform(df_model['severity'])

# ----------------------------
# 7. Feature Columns & Scaling
# ----------------------------
feature_cols = [
    'AGE','GENDER','ETHNICITY','drug_name',
    'dosage_mg','times_administered','treatment_duration_days',
    'INCOME','HEALTHCARE_EXPENSES','HEALTHCARE_COVERAGE','total_cost'
]

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df_model[feature_cols])
y = df_model['severity_encoded']

# ----------------------------
# 8. Train-Test Split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# ----------------------------
# 9. Train Multi-Class Logistic Regression
# ----------------------------
model = LogisticRegression(solver='lbfgs', max_iter=1000)
model.fit(X_train, y_train)

# ----------------------------
# 10. Evaluate Model
# ----------------------------
y_pred = model.predict(X_test)
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=severity_encoder.classes_))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# ----------------------------
# 11. ROC Curves for Multi-Class
# ----------------------------
y_test_bin = label_binarize(y_test, classes=[0,1,2])
y_score = model.predict_proba(X_test)

plt.figure(figsize=(8,6))
for i, class_name in enumerate(severity_encoder.classes_):
    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
    plt.plot(fpr, tpr, label=f"{class_name} (AUC={auc(fpr, tpr):.2f})")

plt.plot([0,1],[0,1],'--', color='gray')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Multi-Class ROC Curve")
plt.legend()
plt.show()

# ----------------------------
# 12. Predict Severity for New Patient
# ----------------------------
def predict_severity(patient_data):
    """
    patient_data: dict with keys matching feature_cols
    Returns: predicted severity name and probability distribution
    """
    df_patient = pd.DataFrame([patient_data])
    
    # Encode categorical features
    for col in ['GENDER','ETHNICITY','drug_name']:
        df_patient[col] = encoders[col].transform(df_patient[col].astype(str))
    
    # Scale features
    df_patient_scaled = scaler.transform(df_patient[feature_cols])
    
    # Predict
    pred_class = model.predict(df_patient_scaled)[0]
    pred_prob = model.predict_proba(df_patient_scaled)[0]
    
    # Convert to readable
    severity_name = severity_encoder.inverse_transform([pred_class])[0]
    severity_prob = {severity_encoder.inverse_transform([i])[0]: round(prob,4) for i, prob in enumerate(pred_prob)}
    
    return severity_name, severity_prob

# Example Usage:
sample_patient = {
    'AGE': 50,
    'GENDER': 'M',
    'ETHNICITY': 'nonhispanic',
    'drug_name': 'Diazepam',
    'dosage_mg': 20,
    'times_administered': 5,
    'treatment_duration_days': 10,
    'INCOME': 40000,
    'HEALTHCARE_EXPENSES': 5000,
    'HEALTHCARE_COVERAGE': 2000,
    'total_cost': 1500
}

severity, prob = predict_severity(sample_patient)
print(f"Predicted Severity: {severity}")
print(f"Probability Distribution: {prob}")
import pickle

# Save everything app.py will need
with open("model.pkl", "wb") as f:
    pickle.dump({
        "model": model,
        "scaler": scaler,
        "encoders": encoders,
        "severity_encoder": severity_encoder,
        "feature_cols": feature_cols
    }, f)

print("Model saved to model.pkl")
