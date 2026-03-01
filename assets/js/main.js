/* ══════════════════════════════════════════
   main.js — Entry point
   Wires up all modules and handles submit.
══════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {

  // Init modules
  initSteps();
  initCostBurden();
  initSeverity();

  // ── Select float-label fix ──
  document.querySelectorAll('select').forEach(sel => {
    sel.addEventListener('change', () => sel.classList.toggle('filled', !!sel.value));
  });

  // ── Form submit ──
  const form      = document.getElementById('patientForm');
  const submitBtn = document.getElementById('submitBtn');
  const toast     = document.getElementById('toast');
  const toastMsg  = document.getElementById('toastMsg');

  function showToast(msg, type = 'success') {
    toastMsg.textContent = msg;
    toast.className = 'toast' + (type === 'warn' ? ' warn' : '');
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Collect raw form values first (for display purposes in renderResult)
    const rawPayload = {
      age:                      form.age.value,
      gender:                   form.gender.value,
      ethnicity:                form.ethnicity.value,
      drug_name:                form.drug_name.value,
      disorder:                 form.disorder.value,
      dosage_mg:                form.dosage_mg.value,
      times_administered:       form.times_administered.value,
      treatment_duration_days:  form.treatment_duration_days.value,
      income:                   form.income.value,
      health_expenses:          form.health_expenses.value,
      health_coverage:          form.health_coverage.value,
      total_cost:               form.total_cost.value,
    };

    // Basic validation — flag any empty required fields
    const missing = Object.entries(rawPayload)
      .filter(([k, v]) => !v)
      .map(([k]) => k.replace(/_/g, ' '));

    if (missing.length > 0) {
      showToast(`Please fill in: ${missing.slice(0,3).join(', ')}${missing.length > 3 ? '…' : ''}`, 'warn');
      return;
    }

    // ── Map to keys the model expects ──
    // HEALTHCARE_COVERAGE: model was trained on numeric values,
    // so we convert the user's text selection to a number
    const coverageMap = {
      'Full':     100,
      'Partial':   60,
      'Medicaid':  80,
      'Medicare':  75,
      'Private':   90,
      'Employer':  85,
      'None':       0
    };

    const mappedPayload = {
      AGE:                     parseFloat(rawPayload.age),
      GENDER:                  rawPayload.gender,
      ETHNICITY:               rawPayload.ethnicity,
      drug_name:               rawPayload.drug_name,
      dosage_mg:               parseFloat(rawPayload.dosage_mg),
      times_administered:      parseFloat(rawPayload.times_administered),
      treatment_duration_days: parseFloat(rawPayload.treatment_duration_days),
      INCOME:                  parseFloat(rawPayload.income),
      HEALTHCARE_EXPENSES:     parseFloat(rawPayload.health_expenses),
      HEALTHCARE_COVERAGE:     coverageMap[rawPayload.health_coverage] ?? 0,
      total_cost:              parseFloat(rawPayload.total_cost)
    };

    // Loading state
    submitBtn.disabled = true;
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
      </svg>
      Analysing…
    `;

    showToast('Sending data to backend…');

    try {
      // Pass the correctly mapped payload to severity.js
      // severity.js will call /predict and render the result
      // rawPayload is also passed so renderResult can display human-readable values
      const result = await window._runSeverityAnalysis(mappedPayload, rawPayload);

      if (!result) throw new Error('No response from backend');

      showToast(`Assessment complete — ${result.severity.toUpperCase()} severity detected`);

    } catch (err) {
      console.error('Severity API error:', err);
      showToast(`Backend error: ${err.message}`, 'warn');
    } finally {
      // Restore button
      submitBtn.disabled = false;
      submitBtn.classList.remove('loading');
      submitBtn.innerHTML = `
        Analyse &amp; Get Severity
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      `;
    }
  });

  // ── Reset ──
  form.addEventListener('reset', () => {
    document.querySelectorAll('select').forEach(s => s.classList.remove('filled'));
    document.getElementById('sec-4').style.display = 'none';
    document.getElementById('costBurdenBar').style.display = 'none';
  });

  // ── New Assessment button ──
  document.getElementById('newAssessmentBtn').addEventListener('click', () => {
    form.reset();
    document.getElementById('sec-4').style.display = 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

});