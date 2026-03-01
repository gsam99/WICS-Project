/* ══════════════════════════════════════════
   severity.js
   Simulates a backend severity prediction.
   In production, replace simulateBackend()
   with a real fetch() call to your API.
══════════════════════════════════════════ */

/* ─────────────────────────────────────────
   MOCK BACKEND
   Replace this with:
     const res  = await fetch('/api/predict', { method:'POST', body: JSON.stringify(payload) });
     const data = await res.json();
   Expected response shape:
   {
     severity: 'low' | 'mid' | 'high',
     score: 0–100,
     confidence: 0–100,
     recommendations: string[]
   }
───────────────────────────────────────── */
function simulateBackend(payload) {
  return new Promise(resolve => {
    setTimeout(() => {

      let score = 0;

      // Age factor (older = higher risk)
      const age = +payload.age || 0;
      if (age > 70)       score += 25;
      else if (age > 55)  score += 15;
      else if (age > 40)  score += 8;
      else                score += 3;

      // Dosage factor
      const mg = +payload.dosage_mg || 0;
      if (mg > 1000)      score += 20;
      else if (mg > 500)  score += 12;
      else if (mg > 100)  score += 6;

      // Duration factor
      const days = +payload.treatment_duration_days || 0;
      if (days > 365)     score += 15;
      else if (days > 90) score += 8;
      else if (days > 30) score += 3;

      // Times administered
      const freq = +payload.times_administered || 0;
      if (freq >= 4)      score += 12;
      else if (freq >= 3) score += 7;
      else if (freq >= 2) score += 3;

      // Financial burden
      const income   = +payload.income || 1;
      const expenses = +payload.health_expenses || 0;
      const total    = +payload.total_cost || 0;
      const spend    = Math.max(expenses, total);
      const burdenPct = (spend / income) * 100;
      if (burdenPct > 40)      score += 18;
      else if (burdenPct > 20) score += 10;
      else if (burdenPct > 10) score += 5;

      // No coverage penalty
      if (payload.health_coverage === 'None') score += 10;

      // High-risk disorders
      const highRisk = ['Cancer','Heart Disease','Alzheimers','COPD','HIV'];
      const midRisk  = ['Diabetes Type 1','Diabetes Type 2','Hypertension','Epilepsy'];
      if (highRisk.includes(payload.disorder))  score += 15;
      else if (midRisk.includes(payload.disorder)) score += 8;

      score = Math.min(score, 100);

      const severity = score >= 60 ? 'high' : score >= 30 ? 'mid' : 'low';

      // Build recommendations
      const recommendations = [];

      if (severity === 'high') {
        recommendations.push('Immediate specialist referral is strongly advised given the combined risk profile.');
        recommendations.push('Consider hospitalisation or intensive outpatient monitoring.');
      }
      if (burdenPct > 25) {
        recommendations.push('Patient may qualify for financial assistance programs — review income-based subsidy eligibility.');
      }
      if (payload.health_coverage === 'None') {
        recommendations.push('Explore Medicaid / ACA marketplace enrollment to reduce out-of-pocket exposure.');
      }
      if (freq >= 4) {
        recommendations.push('High administration frequency detected — evaluate adherence support tools.');
      }
      if (days > 180) {
        recommendations.push('Long-term treatment planned — schedule regular efficacy and safety reviews every 90 days.');
      }
      if (mg > 800) {
        recommendations.push('High dosage flagged — verify dosing protocol and monitor for adverse effects closely.');
      }
      if (recommendations.length === 0) {
        recommendations.push('Patient profile indicates stable risk — maintain current treatment and routine follow-up schedule.');
        recommendations.push('Reassess severity at next scheduled appointment or if symptoms change.');
      }

      resolve({ severity, score, confidence: Math.round(72 + Math.random() * 22), recommendations });
    }, 1800); // simulated network delay
  });
}

/* ─────────────────────────────────────────
   RENDER RESULT
───────────────────────────────────────── */
function renderResult(data, payload) {
  const panel     = document.getElementById('sec-4');
  const resultIcon  = document.getElementById('resultIcon');
  const resultTitle = document.getElementById('resultTitle');
  const sevPill     = document.getElementById('severityPill');
  const gaugeFill   = document.getElementById('gaugeFill');
  const resultGrid  = document.getElementById('resultGrid');
  const recoList    = document.getElementById('recoList');

  const { severity, score, recommendations } = data;

  const labels = { low: 'Low Severity', mid: 'Moderate Severity', high: 'High Severity' };

  // Icon
  resultIcon.className = 'result-icon ' + severity;

  // Title & pill
  resultTitle.textContent = labels[severity];
  sevPill.textContent     = severity.toUpperCase();
  sevPill.className       = 'severity-pill ' + severity;

  // Gauge
  gaugeFill.className    = 'gauge-fill ' + severity;
  setTimeout(() => { gaugeFill.style.width = score + '%'; }, 100);

  // Stats grid
  const accentClass = 'accent-' + severity;

  resultGrid.innerHTML = `
    <div class="result-stat">
      <div class="result-stat-label">Risk Score</div>
      <div class="result-stat-value ${accentClass}">${score}<span style="font-size:0.7em;opacity:0.6"> / 100</span></div>
    </div>
    <div class="result-stat">
      <div class="result-stat-label">Patient Age</div>
      <div class="result-stat-value">${payload.age || '—'} yrs</div>
    </div>
    <div class="result-stat">
      <div class="result-stat-label">Drug / Dosage</div>
      <div class="result-stat-value" style="font-size:0.9rem">${payload.drug_name || '—'} ${payload.dosage_mg ? payload.dosage_mg+'mg' : ''}</div>
    </div>
    <div class="result-stat">
      <div class="result-stat-label">Duration</div>
      <div class="result-stat-value">${payload.treatment_duration_days || '—'} <span style="font-size:0.7em;opacity:0.6">days</span></div>
    </div>
  `;

  // Recommendations
  recoList.innerHTML = recommendations.map(r => `<li>${r}</li>`).join('');

  // Show panel and scroll to it
  panel.style.display = 'block';
  setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

/* ─────────────────────────────────────────
   PUBLIC INIT (called from main.js)
───────────────────────────────────────── */
function initSeverity() {
  // Exposed for main.js to call on submit
  window._runSeverityAnalysis = async function(payload) {
    const data = await simulateBackend(payload);
    renderResult(data, payload);
    return data;
  };
}
