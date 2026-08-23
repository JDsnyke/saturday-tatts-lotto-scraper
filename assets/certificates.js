(() => {
  const nf = new Intl.NumberFormat('en-AU');
  const pct = (value, digits = 3) =>
    new Intl.NumberFormat('en-AU', {
      style: 'percent',
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(Number(value) || 0);
  const pp = (value, digits = 4) => `${(Number(value || 0) * 100).toFixed(digits)} pp`;

  const setText = (id, value) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  };

  function ensureLocalCard() {
    let card = document.getElementById('cert-local-card');
    if (card) return card;
    const grid = document.querySelector('#certificates .planner-kpis');
    if (!grid) return null;
    card = document.createElement('article');
    card.className = 'result-card glass accent';
    card.id = 'cert-local-card';
    card.innerHTML = `
      <div class="console-head"><span>Exact-local refinement</span><span class="badge" id="cert-local-badge">CHECKING</span></div>
      <strong id="cert-local-final">Loading…</strong>
      <small id="cert-local-status">Comparing against the same Coverage start…</small>
    `;
    grid.append(card);
    return card;
  }

  function renderPending() {
    setText('cert-any-exact', 'Pending stats refresh');
    setText('cert-any-exact-status', 'Exact reference result not published yet');
    setText('cert-any-lower', 'Pending stats refresh');
    setText('cert-any-upper', '—');
    setText('cert-d4-exact', 'Pending stats refresh');
    setText('cert-d4-status', '—');
    setText('cert-overlap', '—');
    ensureLocalCard();
    setText('cert-local-final', 'Pending stats refresh');
    setText('cert-local-status', 'Exact-local v2.1.4 reference result not published yet');
    setText('cert-local-badge', 'PENDING');
  }

  function renderLocalSearch(stats) {
    ensureLocalCard();
    const local = stats?.referenceExactLocalSearch;
    const finalExact = local?.finalExactAnyPrize;
    if (!local || !finalExact?.exact) {
      setText('cert-local-final', 'Pending stats refresh');
      setText('cert-local-status', 'Exact-local v2.1.4 reference result not published yet');
      setText('cert-local-badge', 'PENDING');
      return;
    }

    const improvedSets = Number(local.improvementWinningMainSets || 0);
    setText('cert-local-final', pct(finalExact.probability, 4));
    setText(
      'cert-local-status',
      `${improvedSets > 0 ? '+' : ''}${nf.format(improvedSets)} exact winning-main sets · ${improvedSets > 0 ? '+' : ''}${pp(local.improvementProbability)} · ${nf.format(local.acceptedMoves || 0)} accepted move${Number(local.acceptedMoves) === 1 ? '' : 's'}`,
    );
    setText('cert-local-badge', improvedSets > 0 ? 'IMPROVED' : 'NON-WORSE');
  }

  function renderCertificates(stats) {
    const reference = stats?.referenceCoverageSet;
    const metrics = reference?.metrics;
    const certificates = metrics?.probabilityCertificates;
    if (!certificates) {
      renderPending();
      return;
    }

    const anyPrize = certificates.anyPrize;
    const division4 = certificates.division4OrBetter;
    const exactAnyPrize = reference?.exactAnyPrize;

    if (exactAnyPrize?.exact && exactAnyPrize.probability != null) {
      setText('cert-any-exact', pct(exactAnyPrize.probability, 4));
      setText(
        'cert-any-exact-status',
        `${nf.format(exactAnyPrize.anyPrizeWinningMainSets)} of ${nf.format(exactAnyPrize.totalWinningMainSets)} winning-main sets`,
      );
    } else {
      setText('cert-any-exact', 'Pending stats refresh');
      setText('cert-any-exact-status', 'Exact reference result not published yet');
    }

    setText('cert-any-lower', pct(anyPrize.bonferroniLowerBound, 4));
    setText('cert-any-upper', `Union upper bound ${pct(anyPrize.firstOrderUnionBound, 4)}`);
    setText(
      'cert-d4-exact',
      division4.exactProbability == null ? 'Not exact' : pct(division4.exactProbability, 4),
    );
    setText(
      'cert-d4-status',
      division4.globallyOptimalForTicketCount
        ? 'Certified global optimum for this game count'
        : 'Lower bound only; pairwise event intersections remain',
    );
    setText(
      'cert-overlap',
      `${nf.format(metrics.maxPairwiseOverlap)} shared number${metrics.maxPairwiseOverlap === 1 ? '' : 's'}`,
    );

    const badge = document.getElementById('cert-d4-badge');
    if (badge) {
      badge.textContent = division4.globallyOptimalForTicketCount ? 'PROVED OPTIMAL' : 'BOUND ONLY';
    }
    renderLocalSearch(stats);
  }

  async function load() {
    try {
      const response = await fetch('assets/lotto_stats.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      renderCertificates(await response.json());
    } catch (error) {
      console.warn('probability certificates unavailable', error);
      renderPending();
    }
  }

  load();
})();
