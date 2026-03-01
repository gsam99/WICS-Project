/* ══════════════════════════════════════════
   severity.js
   Calls backend Flask API for severity prediction
══════════════════════════════════════════ */

/* ─────────────────────────────────────────
   RENDER RESULT
───────────────────────────────────────── */
function renderResult(data, rawPayload) {
  const panel       = document.getElementById('sec-4');
  const resultIcon  = document.getElementById('resultIcon');
  const resultTitle = document.getElementById('resultTitle');
  const sevPill     = document.getElementById('severityPill');
  const gaugeFill   = document.getElementById('gaugeFill');
  const resultGrid  = document.getElementById('resultGrid');
  const recoList    = document.getElementById('recoList');

  const { severity, confidence, recommendations, score } = data;

  const labels = { low: 'Low Severity', medium: 'Moderate Severity', high: 'High Severity' };

  // Icon
  resultIcon.className = 'result-icon ' + severity;

  // Title & pill
  resultTitle.textContent = labels[severity] || severity;
  sevPill.textContent     = severity.toUpperCase();
  sevPill.className       = 'severity-pill ' + severity;

  // Gauge
  gaugeFill.className = 'gauge-fill ' + severity;
  setTimeout(() => { gaugeFill.style.width = (score || 0) + '%'; }, 100);

  // Stats grid — use rawPayload for human-readable display
  const accentClass = 'accent-' + severity;
  resultGrid.innerHTML = `
    <div class="result-stat">
      <div class="result-stat-label">Confidence</div>
      <div class="result-stat-value ${accentClass}">${confidence || '—'}<span style="font-size:0.7em;opacity:0.6"> %</span></div>
    </div>
    <div class="result-stat">
      <div class="result-stat-label">Patient Age</div>
      <div class="result-stat-value">${rawPayload.age || '—'} yrs</div>
    </div>
    <div class="result-stat">
      <div class="result-stat-label">Drug / Dosage</div>
      <div class="result-stat-value" style="font-size:0.9rem">${rawPayload.drug_name || '—'} ${rawPayload.dosage_mg ? rawPayload.dosage_mg + 'mg' : ''}</div>
    </div>
    <div class="result-stat">
      <div class="result-stat-label">Duration</div>
      <div class="result-stat-value">${rawPayload.treatment_duration_days || '—'} <span style="font-size:0.7em;opacity:0.6">days</span></div>
    </div>
  `;

  // Recommendations
  const recos = recommendations || getDefaultRecommendations(severity);
  recoList.innerHTML = recos.map(r => `<li>${r}</li>`).join('');

  // Show panel and scroll
  panel.style.display = 'block';
  setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
}

/* ─────────────────────────────────────────
   DEFAULT RECOMMENDATIONS BY SEVERITY
───────────────────────────────────────── */
function getDefaultRecommendations(severity) {
  const map = {
    low: [
      'Continue current treatment plan as prescribed.',
      'Schedule routine follow-up in 3–6 months.',
      'Monitor for any changes in symptoms.'
    ],
    medium: [
      'Review dosage with attending physician.',
      'Schedule follow-up within 4–6 weeks.',
      'Consider additional diagnostic tests to monitor progress.',
      'Ensure patient is adhering to medication schedule.'
    ],
    high: [
      'Immediate clinical review recommended.',
      'Consider specialist referral or escalation of care.',
      'Reassess treatment plan and dosage urgently.',
      'Monitor patient closely — daily check-ins advised.',
      'Review financial burden and explore coverage assistance programs.'
    ]
  };
  return map[severity] || ['Severity predicted. Review patient data for further action.'];
}

/* ─────────────────────────────────────────
   CALL BACKEND
───────────────────────────────────────── */
async function callBackend(mappedPayload) {
  const res = await fetch('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(mappedPayload)
  });

  const data = await res.json();

  if (!res.ok || data.error) {
    throw new Error(data.error || 'Unknown backend error');
  }

  // Generate proxy score if backend doesn't provide one
  if (!data.score) {
    data.score = { low: 20, medium: 55, high: 85 }[data.severity] || 0;
  }

  return data;
}

/* ─────────────────────────────────────────
   PUBLIC INIT (called from main.js)
───────────────────────────────────────── */
function initSeverity() {
  // main.js calls this with (mappedPayload, rawPayload)
  window._runSeverityAnalysis = async function(mappedPayload, rawPayload) {
    const data = await callBackend(mappedPayload);
    if (data) renderResult(data, rawPayload || mappedPayload);
    return data;
  };
}