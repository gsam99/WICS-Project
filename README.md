# Inspiration
Adverse drug reactions and medication allergies are a major healthcare risk. Prescriptions are often generalized instead of personalized.

Using drug data from [Kaggle](https://www.kaggle.com/) and synthetic EHR data from [Synthea](https://synthetichealth.github.io/synthea/), we wanted to build a system that predicts medication risk **before complications occur**.

---

# What it does
Our system predicts **drug side effect & allergy risk** in 3 categories:  
**Low**, **Moderate**, **High**

It analyzes:  
- Patient demographics  
- Medication dosage & duration  
- Healthcare costs  
- Medical conditions & allergies

It outputs a **risk level** and **probability distribution** through a simple frontend form.

---

# How we built it
- Merged Kaggle drug data with Synthea EHR data  
- Performed **ETL & feature engineering** (duration, aggregation, encoding, scaling)  
- Built a **Multinomial Logistic Regression** model  
- Evaluated using **confusion matrix** & **ROC curves**  
- Integrated with a **frontend patient intake form** for real-time prediction

---

# Challenges we ran into
- Merging heterogeneous healthcare datasets  
- Cleaning inconsistent date and numeric formats  
- Designing meaningful **severity labels**  
- Handling **multi-class evaluation**  
- Ensuring **encoder/scaler consistency** for live predictions

---

# Accomplishments we're proud of
- Built an **end-to-end ML pipeline**  
- Implemented **multi-class risk scoring**  
- Delivered **real-time frontend + backend integration**  
- Created a **working healthcare AI prototype** within hackathon time

---

#  What we learned
- Data preprocessing is critical in healthcare ML  
- Feature engineering impacts model performance heavily  
- Logistic Regression is interpretable and effective  
- End-to-end integration is essential for practical ML systems

---

# What's next
- Improve severity labeling using clinical guidelines  
- Explore advanced models (XGBoost, Neural Networks)  
- Add model explainability (SHAP)  
- Deploy as a **scalable healthcare API**  
- Integrate into hospital EHR systems for **real-time decision support**
