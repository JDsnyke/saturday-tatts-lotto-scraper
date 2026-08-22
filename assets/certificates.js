(() => {
  const nf = new Intl.NumberFormat('en-AU');
  const pct = (value, digits = 3) =>
    new Intl.NumberFormat('en-AU', {
      style: 'percent',
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(Number(value) || 0);

  const setText = (id, value) => {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  };

  function renderPending() {
    setText('cert-any-exact', 'Pending stats refresh');
    setText('cert-any-exact-status', 'Exact v2.1.3 reference result not published yet');
    setText('cert-any-lower', 'Pending stats refresh');
    setText('cert-any-upper', '—');
    setText('cert-d4-exact', 'Pending stats refresh');
    setText('cert-d4-status', '—');
    setText('cert-overlap', '—');
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
      setText('cert-any-exact-status', 'Exact v2.1.3 reference result not published yet');
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
