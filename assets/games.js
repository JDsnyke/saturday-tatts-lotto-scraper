(() => {
  let games = [];
  let catalogCheckedOn = null;

  const nf = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 2 });
  const pct = new Intl.NumberFormat('en-AU', { style: 'percent', maximumFractionDigits: 8 });
  const money = new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    maximumFractionDigits: 0,
  });
  const mechanicNames = {
    'one-pool': 'Combination draw',
    'two-pool': 'Two-pool draw',
    'ordered-digits': 'Ordered digits',
    'ordered-without-replacement': 'Ordered draw',
    raffle: 'Raffle-style',
    keno: 'Keno / hypergeometric',
    'variable-instant': 'Variable instant',
    'variable-raffle': 'Variable raffle',
  };

  const formatOdds = value =>
    value == null ? 'Variable / unverified' : `1 in ${nf.format(value)}`;

  const escapeHtml = text => String(text ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  function combination(n, k) {
    if (k < 0 || k > n) return 0;
    k = Math.min(k, n - k);
    let value = 1;
    for (let i = 1; i <= k; i += 1) value = value * (n - k + i) / i;
    return value;
  }

  function snapshotMeta(snapshot) {
    if (!snapshot) return '';
    const rows = [];
    if (snapshot.ticketPriceFrom != null) {
      rows.push(`<div><dt>Ticket from</dt><dd>${escapeHtml(money.format(snapshot.ticketPriceFrom))}</dd></div>`);
    }
    if (snapshot.minimumPossibleEntries != null && snapshot.maximumEntries != null) {
      rows.push(
        `<div><dt>Entry range</dt><dd>${nf.format(snapshot.minimumPossibleEntries)}–${nf.format(snapshot.maximumEntries)}</dd></div>`,
      );
    } else if (snapshot.maximumEntries != null) {
      rows.push(`<div><dt>Capacity</dt><dd>Up to ${nf.format(snapshot.maximumEntries)}</dd></div>`);
    }
    if (snapshot.drawDate && snapshot.drawDate !== 'varies') {
      rows.push(`<div><dt>Snapshot draw</dt><dd>${escapeHtml(snapshot.drawDate)}</dd></div>`);
    }
    return rows.join('');
  }

  function renderGames() {
    const operator = document.getElementById('game-operator').value;
    const mechanic = document.getElementById('game-mechanic').value;
    const jurisdiction = document.getElementById('game-jurisdiction').value;
    const sort = document.getElementById('game-sort').value;
    let filtered = games.filter(game =>
      (!operator || game.operator === operator) &&
      (!mechanic || game.mechanic === mechanic) &&
      (!jurisdiction || game.jurisdictions.includes(jurisdiction))
    );

    if (sort === 'odds') {
      filtered = [...filtered].sort((a, b) => {
        const aOdds = a.computedTopOdds ?? a.officialTopOdds ?? Infinity;
        const bOdds = b.computedTopOdds ?? b.officialTopOdds ?? Infinity;
        return aOdds - bOdds;
      });
    } else {
      filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name));
    }

    document.getElementById('game-count').textContent =
      `${filtered.length} option${filtered.length === 1 ? '' : 's'}`;
    document.getElementById('game-grid').innerHTML = filtered.map(game => {
      const topOdds = game.computedTopOdds ?? game.officialTopOdds;
      const anyOdds = game.exactAnyPrizeOdds ?? game.officialAnyOdds;
      const isComputed = game.computedTopOdds != null || game.exactAnyPrizeOdds != null;
      const snapshot = game.raffleSnapshot;
      const note = snapshot?.probabilityNote || game.note || '';
      const sourceUrl = snapshot?.sourceUrl || game.sourceUrl;
      return `
        <article class="game-card glass" data-game="${escapeHtml(game.slug)}">
          <div class="game-card-head">
            <div><span class="eyebrow">${escapeHtml(game.operator)}</span><h3>${escapeHtml(game.name)}</h3></div>
            <span class="claim ${isComputed ? 'exact' : 'guardrail'}">${isComputed ? 'COMPUTED' : 'VARIABLE / REPORTED'}</span>
          </div>
          <p class="game-rule">${escapeHtml(game.description)}</p>
          <div class="odds-pair">
            <div><span>Top / Division 1</span><strong>${formatOdds(topOdds)}</strong></div>
            <div><span>Any prize</span><strong>${formatOdds(anyOdds)}</strong></div>
          </div>
          <dl class="game-meta">
            <div><dt>Mechanic</dt><dd>${escapeHtml(mechanicNames[game.mechanic] || game.mechanic)}</dd></div>
            <div><dt>Where</dt><dd>${escapeHtml(game.jurisdictions.join(', '))}</dd></div>
            <div><dt>Draw</dt><dd>${escapeHtml(game.schedule)}</dd></div>
            ${snapshotMeta(snapshot)}
          </dl>
          ${note ? `<p class="game-note">${escapeHtml(note)}</p>` : ''}
          ${sourceUrl ? `<a class="source-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">Official source ↗</a>` : ''}
        </article>
      `;
    }).join('');
  }

  function renderSetForLife() {
    const draws = Math.max(1, Math.min(365, Number(document.getElementById('sfl-draws').value) || 7));
    const p = 1 / 38320568;
    const cumulative = 1 - ((1 - p) ** draws);
    document.getElementById('sfl-single').textContent = '1 in 38,320,568';
    document.getElementById('sfl-cumulative').textContent = formatOdds(1 / cumulative);
    document.getElementById('sfl-probability').textContent = pct.format(cumulative);
    document.getElementById('sfl-label').textContent =
      `${draws} independent draw${draws === 1 ? '' : 's'}`;
  }

  function renderKeno() {
    const spot = Math.max(1, Math.min(10, Number(document.getElementById('keno-spot').value) || 10));
    const allMatch = combination(80 - spot, 20 - spot) / combination(80, 20);
    document.getElementById('keno-result').textContent = formatOdds(1 / allMatch);
    document.getElementById('keno-probability').textContent = pct.format(allMatch);
    document.getElementById('keno-label').textContent =
      `All ${spot} selected numbers among 20 drawn from 80`;
  }

  function renderCash3() {
    const text = document.getElementById('cash3-digits').value.replace(/\D/g, '').slice(0, 3);
    document.getElementById('cash3-digits').value = text;
    if (text.length !== 3) {
      document.getElementById('cash3-any').textContent = 'Enter 3 digits';
      document.getElementById('cash3-orders').textContent = '—';
      return;
    }
    const unique = new Set(text).size;
    const orderings = unique === 1 ? 1 : unique === 2 ? 3 : 6;
    document.getElementById('cash3-any').textContent = formatOdds(1000 / orderings);
    document.getElementById('cash3-orders').textContent =
      `${orderings} distinct ordering${orderings === 1 ? '' : 's'}`;
  }

  function populateFilters() {
    const operatorSelect = document.getElementById('game-operator');
    [...new Set(games.map(game => game.operator))].sort()
      .forEach(operator => operatorSelect.add(new Option(operator, operator)));
    const mechanicSelect = document.getElementById('game-mechanic');
    [...new Set(games.map(game => game.mechanic))].sort()
      .forEach(mechanic => mechanicSelect.add(new Option(mechanicNames[mechanic] || mechanic, mechanic)));
  }

  async function loadCatalog() {
    const grid = document.getElementById('game-grid');
    try {
      const response = await fetch('assets/game_catalog.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      if (payload.schemaVersion !== 1 || !Array.isArray(payload.games)) {
        throw new Error('unsupported catalog schema');
      }
      games = payload.games;
      catalogCheckedOn = payload.checkedOn;
      populateFilters();
      renderGames();
      const status = document.querySelector('.site-header .data-pill span:last-child');
      if (status && catalogCheckedOn) status.textContent = `Rules checked ${catalogCheckedOn}`;
    } catch (error) {
      console.error('game catalog unavailable', error);
      document.getElementById('game-count').textContent = 'Catalog unavailable';
      grid.innerHTML = '<article class="research-note glass"><div><span class="research-icon">!</span></div><div><h3>Could not load the generated game catalog.</h3><p>The calculators remain available, but game cards are hidden rather than falling back to stale embedded odds.</p></div></article>';
    }
  }

  ['game-operator', 'game-mechanic', 'game-jurisdiction', 'game-sort'].forEach(id =>
    document.getElementById(id).addEventListener('change', renderGames)
  );
  document.getElementById('sfl-draws').addEventListener('input', renderSetForLife);
  document.getElementById('keno-spot').addEventListener('input', renderKeno);
  document.getElementById('cash3-digits').addEventListener('input', renderCash3);

  renderSetForLife();
  renderKeno();
  renderCash3();
  loadCatalog();
})();
