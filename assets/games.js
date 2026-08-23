(() => {
  const games = [
    {
      slug: 'saturday-lotto', name: 'Saturday Lotto / TattsLotto', operator: 'The Lott', mechanic: 'one-pool',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT'], schedule: 'Saturday',
      rule: '6 from 45 + 2 supplementary', topOdds: 8145060, anyOdds: 41.9567300263, computed: true,
      note: 'Exact lower-division engine available. Portfolio optimisation remains Saturday-specific for now.',
      source: 'https://help.thelott.com/hc/en-us/articles/4416859880985-How-do-I-play-the-Saturday-lotto-game'
    },
    {
      slug: 'weekday-windfall', name: 'Weekday Windfall', operator: 'The Lott', mechanic: 'one-pool',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT'], schedule: 'Mon / Wed / Fri',
      rule: '6 from 45 + 2 supplementary', topOdds: 8145060, anyOdds: null, computed: true,
      note: 'Division 1 is exact from the verified 6/45 mechanic. A current aggregate any-prize figure is not shown until separately re-verified.',
      source: 'https://help.thelott.com/hc/en-us/articles/34129397583513-How-do-I-play-the-Weekday-Windfall-game'
    },
    {
      slug: 'oz-lotto', name: 'Oz Lotto', operator: 'The Lott', mechanic: 'one-pool',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT', 'WA'], schedule: 'Tuesday',
      rule: '7 from 47 + 3 supplementary', topOdds: 62891499, anyOdds: 50.3318823947, computed: true,
      note: 'Exact one-pool match distribution with a seven-number main selection.',
      source: 'https://help.thelott.com/hc/en-us/articles/4416863329689-How-do-I-play-the-Oz-Lotto-game'
    },
    {
      slug: 'powerball', name: 'Powerball', operator: 'The Lott', mechanic: 'two-pool',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT', 'WA'], schedule: 'Thursday',
      rule: '7 from 35 × 1 Powerball from 20', topOdds: 134490400, anyOdds: 43.9817977576, computed: true,
      note: 'Two independent pools. Division 1 denominator is C(35,7) × 20.',
      source: 'https://help.thelott.com/hc/en-us/articles/4416863320217-How-do-I-play-the-Powerball-game'
    },
    {
      slug: 'set-for-life', name: 'Set for Life', operator: 'The Lott', mechanic: 'one-pool',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT', 'WA'], schedule: 'Daily · standard entry spans 7 draws',
      rule: '7 from 44 + 2 supplementary', topOdds: 38320568, anyOdds: 50.0810511637, computed: true,
      note: 'The per-draw odds and cumulative chance over the seven included independent draws are different quantities.',
      source: 'https://help.thelott.com/hc/en-us/articles/4416859752601-How-do-I-play-the-Set-for-Life-game'
    },
    {
      slug: 'super-66', name: 'Super 66', operator: 'The Lott', mechanic: 'ordered-digits',
      jurisdictions: ['QLD', 'VIC', 'TAS', 'SA', 'NT', 'WA'], schedule: 'Saturday',
      rule: '6 ordered digits · 10 possibilities each', topOdds: 1000000, anyOdds: 51, computed: true,
      note: 'An ordered-digit game, not a choose-k combination lottery. Overall odds are current Lotterywest-reported national game odds.',
      source: 'https://www.lotterywest.wa.gov.au/games/super-66'
    },
    {
      slug: 'lotto-strike', name: 'Lotto Strike', operator: 'The Lott', mechanic: 'ordered-without-replacement',
      jurisdictions: ['NSW', 'ACT'], schedule: 'Mon / Wed / Fri / Sat add-on',
      rule: 'First 4 Lotto balls in exact order', topOdds: 3575880, anyOdds: null, computed: true,
      note: 'Top odds are 45P4, not C(45,4). Aggregate any-prize odds are withheld until current full division semantics are separately captured.',
      source: 'https://help.thelott.com/hc/en-us/articles/4416863538969-How-do-I-play-the-Lotto-Strike-game'
    },
    {
      slug: 'lucky-lotteries-super', name: 'Lucky Lotteries Super Jackpot', operator: 'The Lott', mechanic: 'raffle',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT'], schedule: 'When ticket pool sells out',
      rule: 'Finite raffle pool + separate jackpot draw', topOdds: 18385877, anyOdds: null, computed: false,
      note: 'Current jackpot odds are operator-reported. No stale aggregate any-prize figure is carried forward.',
      source: 'https://help.thelott.com/hc/en-us/articles/35525459564441-What-are-the-odds-of-each-game'
    },
    {
      slug: 'lucky-lotteries-mega', name: 'Lucky Lotteries Mega Jackpot', operator: 'The Lott', mechanic: 'raffle',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT'], schedule: 'When ticket pool sells out',
      rule: 'Finite raffle pool + separate jackpot draw', topOdds: 9483168, anyOdds: null, computed: false,
      note: 'Current jackpot odds are operator-reported. The game is not represented as a combination-selection draw.',
      source: 'https://help.thelott.com/hc/en-us/articles/35525459564441-What-are-the-odds-of-each-game'
    },
    {
      slug: 'keno-sa', name: 'Keno', operator: 'The Lott', mechanic: 'keno',
      jurisdictions: ['SA'], schedule: 'Every few minutes',
      rule: '20 drawn from 80 · Spot 1–10', topOdds: null, anyOdds: null, computed: true,
      note: 'SA-only through The Lott. Use the Spot calculator because the relevant probability changes with Spot size and prize condition.',
      source: 'https://help.thelott.com/hc/en-us/articles/4416859934873-How-do-I-play-the-Keno-game'
    },
    {
      slug: 'instant-scratch-its', name: 'Instant Scratch-Its', operator: 'The Lott', mechanic: 'variable-instant',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'TAS', 'SA', 'NT'], schedule: 'Instant product family',
      rule: 'Varies by printed game', topOdds: null, anyOdds: 4, computed: false,
      note: 'The Lott currently reports about 1 in 4 for any prize; top-prize odds vary by the specific ticket.',
      source: 'https://help.thelott.com/hc/en-us/articles/35525459564441-What-are-the-odds-of-each-game'
    },
    {
      slug: 'play-for-purpose', name: 'Play For Purpose charity raffle', operator: 'Play For Purpose / The Lott platform', mechanic: 'variable-raffle',
      jurisdictions: ['Australia · raffle terms apply'], schedule: 'Varies by raffle',
      rule: 'Ticket-supply-dependent charity raffle', topOdds: null, anyOdds: null, computed: false,
      note: 'The operator states odds depend on the number of tickets sold, so no fixed denominator is invented.',
      source: 'https://help.thelott.com/hc/en-us/articles/35525459564441-What-are-the-odds-of-each-game'
    },
    {
      slug: 'millionaire-medley', name: 'Millionaire Medley', operator: 'Lotterywest', mechanic: 'one-pool',
      jurisdictions: ['WA'], schedule: 'Mon / Wed / Fri',
      rule: '6 from 45 + 2 supplementary', topOdds: 8145060, anyOdds: 85.4317180617, computed: true,
      note: 'Same 6/45 draw geometry as Saturday Lotto but a different lower-division prize mapping.',
      source: 'https://www.lotterywest.wa.gov.au/games/millionaire-medley'
    },
    {
      slug: 'cash-3', name: 'Cash 3', operator: 'Lotterywest', mechanic: 'ordered-digits',
      jurisdictions: ['WA'], schedule: 'Daily',
      rule: '3 ordered digits · Exact / Any Order', topOdds: 1000, anyOdds: null, computed: true,
      note: 'Exact Order is 1 in 1,000. Any Order depends on the number of distinct permutations of the chosen digits.',
      source: 'https://www.lotterywest.wa.gov.au/games/cash-3'
    },
    {
      slug: 'scratch-n-win', name: "Scratch'n'Win", operator: 'Lotterywest', mechanic: 'variable-instant',
      jurisdictions: ['WA'], schedule: 'Instant product family',
      rule: 'Varies by printed game', topOdds: null, anyOdds: null, computed: false,
      note: 'Prize tables and top-prize odds vary by ticket design and print run.',
      source: 'https://www.lotterywest.wa.gov.au/games/games-to-play'
    },
    {
      slug: 'yourtown-prize-home', name: 'yourtown Prize Home Draws', operator: 'yourtown', mechanic: 'variable-raffle',
      jurisdictions: ['Australia · draw terms apply'], schedule: 'Recurring Prize Home draws',
      rule: 'Art union · First Prize odds depend on tickets sold', topOdds: null, anyOdds: null, computed: false,
      capacity: 'Most Prize Home draws: 500,000 tickets available', price: 'Usually $15/ticket',
      note: 'yourtown explicitly says 1 in 500,000 is the sold-out one-ticket example; if fewer tickets sell, the denominator is lower.',
      source: 'https://support.yourtown.com.au/hc/en-us/articles/360000830493-What-are-the-odds-of-winning-First-Prize'
    },
    {
      slug: 'mater-prize-home', name: 'Mater Prize Home', operator: 'Mater Lotteries', mechanic: 'variable-raffle',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'NT'], schedule: 'Draw 327 · 23 Oct 2026',
      rule: 'Prize Home art union with bundle-dependent entry count', topOdds: null, anyOdds: null, computed: false,
      capacity: 'Draw 327: 13,455,147–22,805,334 possible entries', price: 'Tickets from $2',
      note: 'The current terms give an entry-count range because bundles create bonus entries. That range is not collapsed into one fake odds denominator.',
      source: 'https://www.materlotteries.com.au/mater-prize-home/terms-and-conditions/327'
    },
    {
      slug: 'mater-cars-for-cancer', name: 'Mater Cars for Cancer', operator: 'Mater Lotteries', mechanic: 'variable-raffle',
      jurisdictions: ['QLD', 'NSW', 'ACT', 'VIC', 'SA', 'NT'], schedule: 'Draw 130 · 16 Sep 2026',
      rule: 'Vehicle/lifestyle prize lottery', topOdds: null, anyOdds: null, computed: false,
      capacity: 'Draw 130: up to 85,117 tickets', price: '$30/ticket',
      note: 'The current draw offers a $510,707 main prize package. The permitted ticket cap is shown as scarcity metadata, not assumed final valid-entry odds.',
      source: 'https://www.materlotteries.com.au/mater-cars-for-cancer/terms-and-conditions/130'
    },
    {
      slug: 'dream-home-art-union', name: 'Dream Home Art Union', operator: 'RSL Queensland', mechanic: 'variable-raffle',
      jurisdictions: ['Australia · draw permits apply'], schedule: 'Draw 434 · 20 Oct 2026',
      rule: 'Recurring prize-home art union', topOdds: null, anyOdds: null, computed: false,
      capacity: 'Draw-specific entry capacity', price: 'Tickets from $5',
      note: 'Formerly RSL Art Union. Current Draw 434 offers a $10.2M Currumbin Gold Coast package; exact odds stay variable until draw-specific entry-capacity terms are captured.',
      source: 'https://dreamhomeartunion.com.au/'
    },
    {
      slug: 'endeavour-prize-home', name: 'Endeavour Foundation Prize Home', operator: 'Endeavour Lotteries', mechanic: 'variable-raffle',
      jurisdictions: ['Australia · draw terms apply'], schedule: 'Recurring Prize Home draws',
      rule: 'Prize Home art union with bundle bonus tickets', topOdds: null, anyOdds: null, computed: false,
      capacity: 'Draw-specific', price: 'Recent Draw 468 tickets from $10',
      note: 'Recent Draw 468 was drawn 20 Aug 2026. Bundle bonuses mean dollars spent are not a universal probability denominator.',
      source: 'https://www.endeavourlotteries.com.au/endeavour-foundation/terms-and-conditions'
    },
    {
      slug: 'endeavour-pay-day', name: 'Endeavour Pay Day', operator: 'Endeavour Lotteries', mechanic: 'variable-raffle',
      jurisdictions: ['Australia · eligibility terms apply'], schedule: 'Draw 221 · 8 Oct 2026',
      rule: 'Cash/vehicle prize draw', topOdds: null, anyOdds: null, computed: false,
      capacity: 'Draw 221: limited to 200,000 tickets', price: '$5/ticket',
      note: 'Current first prize is $200K gold or a vehicle/gold package. The 200,000-ticket cap is shown as capacity, not silently treated as final odds.',
      source: 'https://www.endeavourlotteries.com.au/pay-day/terms-and-conditions/221'
    }
  ];

  const nf = new Intl.NumberFormat('en-AU', { maximumFractionDigits: 2 });
  const pct = new Intl.NumberFormat('en-AU', { style: 'percent', maximumFractionDigits: 8 });
  const mechanicNames = {
    'one-pool': 'Combination draw',
    'two-pool': 'Two-pool draw',
    'ordered-digits': 'Ordered digits',
    'ordered-without-replacement': 'Ordered draw',
    raffle: 'Raffle-style',
    keno: 'Keno / hypergeometric',
    'variable-instant': 'Variable instant',
    'variable-raffle': 'Variable raffle'
  };

  const formatOdds = value => value == null ? 'Variable / draw-specific' : `1 in ${nf.format(value)}`;
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
      filtered = [...filtered].sort((a, b) => (a.topOdds ?? Infinity) - (b.topOdds ?? Infinity));
    } else {
      filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name));
    }

    document.getElementById('game-count').textContent = `${filtered.length} option${filtered.length === 1 ? '' : 's'}`;
    document.getElementById('game-grid').innerHTML = filtered.map(game => `
      <article class="game-card glass" data-game="${escapeHtml(game.slug)}">
        <div class="game-card-head">
          <div><span class="eyebrow">${escapeHtml(game.operator)}</span><h3>${escapeHtml(game.name)}</h3></div>
          <span class="claim ${game.computed ? 'exact' : 'guardrail'}">${game.computed ? 'COMPUTED' : 'VARIABLE / REPORTED'}</span>
        </div>
        <p class="game-rule">${escapeHtml(game.rule)}</p>
        <div class="odds-pair">
          <div><span>Top / Division 1</span><strong>${formatOdds(game.topOdds)}</strong></div>
          <div><span>Any prize</span><strong>${formatOdds(game.anyOdds)}</strong></div>
        </div>
        <dl class="game-meta">
          <div><dt>Mechanic</dt><dd>${escapeHtml(mechanicNames[game.mechanic])}</dd></div>
          <div><dt>Where</dt><dd>${escapeHtml(game.jurisdictions.join(', '))}</dd></div>
          <div><dt>Draw</dt><dd>${escapeHtml(game.schedule)}</dd></div>
          ${game.price ? `<div><dt>Price</dt><dd>${escapeHtml(game.price)}</dd></div>` : ''}
          ${game.capacity ? `<div><dt>Capacity</dt><dd>${escapeHtml(game.capacity)}</dd></div>` : ''}
        </dl>
        <p class="game-note">${escapeHtml(game.note)}</p>
        <a class="source-link" href="${escapeHtml(game.source)}" target="_blank" rel="noreferrer">Official source ↗</a>
      </article>
    `).join('');
  }

  function renderSetForLife() {
    const draws = Math.max(1, Math.min(365, Number(document.getElementById('sfl-draws').value) || 7));
    const p = 1 / 38320568;
    const cumulative = 1 - ((1 - p) ** draws);
    document.getElementById('sfl-single').textContent = '1 in 38,320,568';
    document.getElementById('sfl-cumulative').textContent = formatOdds(1 / cumulative);
    document.getElementById('sfl-probability').textContent = pct.format(cumulative);
    document.getElementById('sfl-label').textContent = `${draws} independent draw${draws === 1 ? '' : 's'}`;
  }

  function renderKeno() {
    const spot = Math.max(1, Math.min(10, Number(document.getElementById('keno-spot').value) || 10));
    const allMatch = combination(80 - spot, 20 - spot) / combination(80, 20);
    document.getElementById('keno-result').textContent = formatOdds(1 / allMatch);
    document.getElementById('keno-probability').textContent = pct.format(allMatch);
    document.getElementById('keno-label').textContent = `All ${spot} selected numbers among 20 drawn from 80`;
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
    document.getElementById('cash3-orders').textContent = `${orderings} distinct ordering${orderings === 1 ? '' : 's'}`;
  }

  function populateFilters() {
    const operatorSelect = document.getElementById('game-operator');
    [...new Set(games.map(game => game.operator))].sort()
      .forEach(operator => operatorSelect.add(new Option(operator, operator)));
    const mechanicSelect = document.getElementById('game-mechanic');
    [...new Set(games.map(game => game.mechanic))].sort()
      .forEach(mechanic => mechanicSelect.add(new Option(mechanicNames[mechanic], mechanic)));
  }

  populateFilters();
  ['game-operator', 'game-mechanic', 'game-jurisdiction', 'game-sort'].forEach(id =>
    document.getElementById(id).addEventListener('change', renderGames)
  );
  document.getElementById('sfl-draws').addEventListener('input', renderSetForLife);
  document.getElementById('keno-spot').addEventListener('input', renderKeno);
  document.getElementById('cash3-digits').addEventListener('input', renderCash3);
  renderGames();
  renderSetForLife();
  renderKeno();
  renderCash3();
})();
