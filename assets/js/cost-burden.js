/* ══════════════════════════════════════════
   cost-burden.js
   Live cost burden indicator.
   Shows health expenses as % of income and
   colours the bar green / amber / red.
══════════════════════════════════════════ */
function initCostBurden() {
  const incomeEl   = document.getElementById('income');
  const expenseEl  = document.getElementById('health_expenses');
  const totalEl    = document.getElementById('total_cost');
  const barWrap    = document.getElementById('costBurdenBar');
  const burdenFill = document.getElementById('burdenFill');
  const burdenPct  = document.getElementById('burdenPct');
  const burdenDesc = document.getElementById('burdenDesc');

  if (!incomeEl || !barWrap) return;

  function update() {
    const income   = parseFloat(incomeEl.value)  || 0;
    const expenses = parseFloat(expenseEl.value) || 0;
    const total    = parseFloat(totalEl.value)   || 0;

    // Use the larger of annual expenses vs total treatment cost
    const totalSpend = Math.max(expenses, total);

    if (income <= 0 || totalSpend <= 0) {
      barWrap.style.display = 'none';
      return;
    }

    barWrap.style.display = 'block';

    const pct = Math.min((totalSpend / income) * 100, 100);
    burdenFill.style.width = pct + '%';
    burdenPct.textContent  = pct.toFixed(1) + '%';

    if (pct < 10) {
      burdenFill.style.background = 'linear-gradient(90deg,#166534,#4ade80)';
      burdenDesc.textContent = '✓ Low burden — healthcare costs are a manageable share of income.';
      burdenDesc.style.color = '#4ade80';
    } else if (pct < 25) {
      burdenFill.style.background = 'linear-gradient(90deg,#92400e,#fbbf24)';
      burdenDesc.textContent = '⚠ Moderate burden — costs represent a notable share of annual income.';
      burdenDesc.style.color = '#fbbf24';
    } else {
      burdenFill.style.background = 'linear-gradient(90deg,#991b1b,#f87171)';
      burdenDesc.textContent = '✕ High burden — healthcare costs exceed 25% of income. Financial assistance may be needed.';
      burdenDesc.style.color = '#f87171';
    }
  }

  [incomeEl, expenseEl, totalEl].forEach(el => el && el.addEventListener('input', update));
}
