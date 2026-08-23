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
  const mechanicIcons = {
    'one-pool': 'circle-dot-dashed',
    'two-pool': 'split',
    'ordered-digits': 'hash',
    'ordered-without-replacement': 'list-ordered',
    raffle: 'ticket-check',
    keno: 'circle-dot',
    'variable-instant': 'badge-dollar-sign',
    'variable-raffle': 'tickets',
  };

  const formatOdds = value => value == null ? 'Variable / unverified' : `1 in ${nf.format(value)}`;
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

  function snapshotRows(snapshot) {
    if (!snapshot) return '';
    const rows = [];
    if (snapshot.ticketPriceFrom != null) {
      rows.push(`<tr><th>Ticket from</th><td>${escapeHtml(money.format(snapshot.ticketPriceFrom))}</td></tr>`);
    }
    if (snapshot.minimumPossibleEntries != null && snapshot.maximumEntries != null) {
      rows.push(`<tr><th>Entry range</th><td>${nf.format(snapshot.minimumPossibleEntries)}–${nf.format(snapshot.maximumEntries)}</td></tr>`);
    } else if (snapshot.maximumEntries != null) {
      rows.push(`<tr><th>Capacity</th><td>Up to ${nf.format(snapshot.maximumEntries)}</td></tr>`);
    }
    if (snapshot.drawDate && snapshot.drawDate !== 'varies') {
      rows.push(`<tr><th>Snapshot draw</th><td>${escapeHtml(snapshot.drawDate)}</td></tr>`);
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

    document.getElementById('game-count').textContent = `${filtered.length} option${filtered.length === 1 ? '' : 's'}`;
    document.getElementById('game-grid').innerHTML = filtered.map(game => {
      const topOdds = game.computedTopOdds ?? game.officialTopOdds;
      const anyOdds = game.exactAnyPrizeOdds ?? game.officialAnyOdds;
      const isComputed = game.computedTopOdds != null || game.exactAnyPrizeOdds != null;
      const snapshot = game.raffleSnapshot;
      const note = snapshot?.probabilityNote || game.note || '';
      const sourceUrl = snapshot?.sourceUrl || game.sourceUrl;
      const icon = mechanicIcons[game.mechanic] || 'circle-help';
      return `
        <div class="column is-half" data-game="${escapeHtml(game.slug)}">
          <article class="card">
            <div class="card-content">
              <div class="media">
                <div class="media-left"><span class="icon is-large"><i data-lucide="${icon}"></i></span></div>
                <div class="media-content"><p class="title is-5">${escapeHtml(game.name)}</p><p class="subtitle is-7">${escapeHtml(game.operator)}</p></div>
                <div class="media-right"><span class="tag ${isComputed ? 'is-success' : 'is-warning'} is-light">${isComputed ? 'Computed' : 'Variable / reported'}</span></div>
              </div>
              <div class="content">
                <p>${escapeHtml(game.description)}</p>
                <div class="columns is-mobile">
                  <div class="column"><p class="heading">Top / Division 1</p><p class="title is-6">${formatOdds(topOdds)}</p></div>
                  <div class="column"><p class="heading">Any prize</p><p class="title is-6">${formatOdds(anyOdds)}</p></div>
                </div>
                <div class="table-container"><table class="table is-fullwidth is-narrow"><tbody>
                  <tr><th>Mechanic</th><td>${escapeHtml(mechanicNames[game.mechanic] || game.mechanic)}</td></tr>
                  <tr><th>Where</th><td>${escapeHtml(game.jurisdictions.join(', '))}</td></tr>
                  <tr><th>Draw</th><td>${escapeHtml(game.schedule)}</td></tr>
                  ${snapshotRows(snapshot)}
                </tbody></table></div>
                ${note ? `<div class="notification is-light">${escapeHtml(note)}</div>` : ''}
                ${sourceUrl ? `<a class="button is-small is-link is-light" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer"><span class="icon"><i data-lucide="external-link"></i></span><span>Official source</span></a>` : ''}
              </div>
            </div>
          </article>
        </div>`;
    }).join('');
    window.refreshIcons?.();
  }

  function renderSetForLife() {
    const input = document.getElementById('sfl-draws');
    const draws = Math.max(1, Math.min(365, Number(input.value) || 7));
    input.value = draws;
    const p = 1 / 38_320_568;
    const cumulative = 1 - ((1 - p) ** draws);
    document.getElementById('sfl-single').textContent = '1 in 38,320,568';
    document.getElementById('sfl-cumulative').textContent = formatOdds(1 / cumulative);
    document.getElementById('sfl-probability').textContent = pct.format(cumulative);
    document.getElementById('sfl-label').textContent = `${draws} independent draw${draws === 1 ? '' : 's'}`;
  }

  function renderKeno() {
    const input = document.getElementById('keno-spot');
    const spot = Math.max(1, Math.min(10, Number(input.value) || 10));
    input.value = spot;
    const allMatch = combination(80 - spot, 20 - spot) / combination(80, 20);
    document.getElementById('keno-result').textContent = formatOdds(1 / allMatch);
    document.getElementById('keno-probability').textContent = pct.format(allMatch);
    document.getElementById('keno-label').textContent = `All ${spot} selected numbers among 20 drawn from 80`;
  }

  function renderCash3() {
    const input = document.getElementById('cash3-digits');
    const text = input.value.replace(/\D/g, '').slice(0, 3);
    input.value = text;
    if (text.length !== 3) {
      document.getElementById('cash3-any').textContent = 'Enter 3 digits';
      document.getElementById('cash3-orders').textContent = '—';
      return;
    }
    const unique = new Set(text).size;
    const orderings = unique === 1 ? 1 : unique === 2 ? 3 : 6;
    document.getElementById('cash3-any').textContent = formatOdds(1000 / orderings);
    document.getElementById('cash3-orders').textContent = `${orderings} distinct ordering${orderings === 1 ? '' : 's'}`;
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
    const status = document.getElementById('catalog-status');
    try {
      const response = await fetch('assets/game_catalog.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      if (payload.schemaVersion !== 1 || !Array.isArray(payload.games)) throw new Error('unsupported catalog schema');
      games = payload.games;
      catalogCheckedOn = payload.checkedOn;
      populateFilters();
      renderGames();
      status.classList.remove('is-skeleton');
      status.textContent = catalogCheckedOn ? `Rules checked ${catalogCheckedOn}` : 'Rules loaded';
      window.clearSkeletons?.(grid);
    } catch (error) {
      console.error('game catalog unavailable', error);
      document.getElementById('game-count').textContent = 'Catalog unavailable';
      status.classList.remove('is-skeleton', 'is-info');
      status.classList.add('is-danger');
      status.textContent = 'Catalog unavailable';
      grid.innerHTML = '<div class="column"><article class="message is-danger"><div class="message-header"><p>Catalog unavailable</p></div><div class="message-body">The calculators remain available, but game cards are hidden rather than falling back to stale embedded odds.</div></article></div>';
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
