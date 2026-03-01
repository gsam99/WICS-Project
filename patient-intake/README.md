# MedChart · Patient Intake & Severity Assessment

A dark-themed clinical intake form with live severity prediction. All fields map directly to a backend ML/prediction API.

---

## Folder Structure

```
patient-intake/
│
├── index.html
├── README.md
│
└── assets/
    ├── css/
    │   ├── style.css          ← CSS variables, reset
    │   ├── layout.css         ← Sidebar, container, grids, responsive
    │   ├── components.css     ← Cards, fields, buttons, result panel
    │   └── animations.css     ← Blobs, keyframes
    │
    └── js/
        ├── main.js            ← Entry point & form submit handler
        ├── steps.js           ← Sidebar step scroll sync
        ├── cost-burden.js     ← Live cost-to-income ratio bar
        └── severity.js        ← Severity engine (mock → replace with fetch)
```

---

## Fields Collected

| Field | Type | Notes |
|---|---|---|
| `age` | number | Patient age |
| `gender` | select | Male / Female / Other … |
| `ethnicity` | select | Full list |
| `drug_name` | text | e.g. Metformin |
| `disorder` | select | 14 diagnoses |
| `dosage_mg` | number | Dosage in milligrams |
| `times_administered` | number | Per day |
| `treatment_duration_days` | number | Total days |
| `income` | number | Annual USD |
| `health_expenses` | number | Annual USD |
| `health_coverage` | select | Insurance type |
| `total_cost` | number | Treatment cost USD |

---

## Connecting to Your Backend

In `assets/js/severity.js`, replace `simulateBackend()` with:

```js
async function callBackend(payload) {
  const res = await fetch('https://your-api.com/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
  // Expected: { severity: 'low'|'mid'|'high', score: 0-100, confidence: 0-100, recommendations: string[] }
}
```

---

## Running Locally

**Option 1 — Live Server (VS Code)**
1. Install the **Live Server** extension
2. Right-click `index.html` → **Open with Live Server**
3. Opens at `http://127.0.0.1:5500`

**Option 2 — Python**
```bash
python -m http.server 8000
# open http://localhost:8000
```

**Option 3 — Node**
```bash
npx serve .
# open http://localhost:3000
```
