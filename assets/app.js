const BALL_COUNT = 45;
const MAIN_COUNT = 6;
const DIV1_COMBINATIONS = 8_145_060;
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const nf = new Intl.NumberFormat('en-AU');
const pct = (value, digits = 4) => new Intl.NumberFormat('en-AU', {
  style: 'percent',
  minimumFractionDigits: digits,
  maximumFractionDigits: Math.max(digits, 8),
}).format(value || 0);
let state = { stats: null, provenance: null, tickets: [], filteredDraws: [], drawLimit: 30 };

function comb(n, k) {
  if (k < 0 || k > n) return 0;
  k = Math.min(k, n - k);
  let result = 1;
  for (let i = 1; i <= k; i += 1) result = result * (n - k + i) / i;
  return Math.round(result);
}
function odds(probability) { return probability > 0 ? 1 / probability : Infinity; }
function fmtOdds(probability) {
  const value = odds(probability);
  return Number.isFinite(value)
    ? `1 in ${value < 100 ? value.toFixed(2) : nf.format(Math.round(value))}`
    : '—';
}
function categoryProbability(main, supplementary) {
  const other = MAIN_COUNT - main - supplementary;
  if (other < 0 || other > 37) return 0;
  return comb(6, main) * comb(2, supplementary) * comb(37, other) / DIV1_COMBINATIONS;
}
function exactPrizeRows() {
  return [
    { division: 1, requirement: '6 winning', probability: categoryProbability(6, 0) },
    { division: 2, requirement: '5 winning + supplementary', probability: categoryProbability(5, 1) },
    { division: 3, requirement: '5 winning', probability: categoryProbability(5, 0) },
    { division: 4, requirement: '4 winning', probability: [0, 1, 2].reduce((a, s) => a + categoryProbability(4, s), 0) },
    { division: 5, requirement: '3 winning + supplementary', probability: categoryProbability(3, 1) + categoryProbability(3, 2) },
    { division: 6, requirement: '3 winning', probability: categoryProbability(3, 0) },
  ].map(row => ({ ...row, odds: odds(row.probability) }));
}
function exactMatchRows() {
  return Array.from({ length: 7 }, (_, matches) => ({
    matches,
    probability: comb(6, matches) * comb(39, 6 - matches) / DIV1_COMBINATIONS,
  }));
}
function toast(message) {
  const element = $('#toast');
  element.textContent = message;
  element.classList.remove('is-hidden');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => element.classList.add('is-hidden'), 2200);
}

function setupTabs() {
  $$('.tabs [data-tab]').forEach(tab => tab.addEventListener('click', event => {
    event.preventDefault();
    const target = tab.dataset.tab;
    $$('.tabs [data-tab]').forEach(item => item.parentElement.classList.toggle('is-active', item === tab));
    ['frequency', 'pairs', 'quality'].forEach(name => {
      $(`#panel-${name}`)?.classList.toggle('is-hidden', name !== target);
    });
  }));
}

async function loadJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.json();
}
function normalizeStats(raw) {
  if (raw?.schemaVersion === 3) return raw;
  if (raw?.schemaVersion === 2) {
    return {
      ...raw,
      probabilityModel: {
        prizeDivisions: exactPrizeRows(),
        anyPrizeProbability: exactPrizeRows().reduce((a, row) => a + row.probability, 0),
        mainMatchDistribution: exactMatchRows(),
        systemEntries: [],
      },
      draws: raw.draws || [],
      referenceSimulation: null,
      referenceBacktest: null,
      legacyWarning: true,
    };
  }
  const frequencies = raw?.allFrequencies?.winning || Array(45).fill(0);
  const total = frequencies.reduce((a, b) => a + Number(b || 0), 0);
  const drawCount = total && total % 6 === 0 ? total / 6 : Number(raw?.summary?.totalDraws || 0);
  const expected = drawCount * 6 / 45;
  const probability = 6 / 45;
  const variance = drawCount * probability * (1 - probability);
  const z = frequencies.map(count => variance ? (count - expected) / Math.sqrt(variance) : 0);
  const dates = [raw?.summary?.dateRange?.first, raw?.summary?.dateRange?.last].filter(Boolean).sort();
  return {
    schemaVersion: 1,
    generatedAt: raw?.lastUpdated || null,
    game: { divisionOneCombinations: DIV1_COMBINATIONS },
    dataset: {
      drawCount,
      firstDraw: dates.length === 2 && dates[0] === raw?.summary?.dateRange?.first ? dates[0] : null,
      lastDraw: dates.at(-1) || null,
      mainObservations: total,
    },
    probabilityModel: {
      prizeDivisions: exactPrizeRows(),
      anyPrizeProbability: exactPrizeRows().reduce((a, row) => a + row.probability, 0),
      mainMatchDistribution: exactMatchRows(),
      systemEntries: [],
    },
    fairnessDiagnostics: {
      expectedMainCountPerNumber: expected,
      normalizedEntropy: entropy(frequencies),
      maxAbsoluteZScore: Math.max(0, ...z.map(Math.abs)),
      chiSquareUniform: expected ? frequencies.reduce((a, count) => a + (count - expected) ** 2 / expected, 0) : 0,
    },
    numbers: frequencies.map((count, index) => ({ number: index + 1, mainCount: count, zScore: z[index] })),
    topHistoricalPairs: [],
    draws: [],
    referenceSimulation: null,
    referenceBacktest: null,
    legacyWarning: true,
  };
}
function entropy(values) {
  const total = values.reduce((a, b) => a + b, 0);
  if (!total) return 0;
  return -values.filter(Boolean).reduce((sum, count) => {
    const q = count / total;
    return sum + q * Math.log(q);
  }, 0) / Math.log(values.length);
}
async function loadData() {
  let stats;
  try { stats = normalizeStats(await loadJson('assets/lotto_stats.json')); }
  catch (error) { console.error(error); stats = normalizeStats({}); }
  let provenance = null;
  try { provenance = await loadJson('assets/data_provenance.json'); }
  catch (error) { console.warn(error); }
  state.stats = stats;
  state.provenance = provenance;
  renderCore();
  renderPlanner();
  renderEvidence();
  renderDrawExplorer();
  renderDiagnostics();
  window.clearSkeletons?.();
  window.refreshIcons?.();
}

function renderCore() {
  const stats = state.stats;
  const combinations = stats.game?.divisionOneCombinations || DIV1_COMBINATIONS;
  const anyPrize = stats.probabilityModel?.anyPrizeProbability || exactPrizeRows().reduce((a, row) => a + row.probability, 0);
  $('#hero-odds').textContent = `1 in ${nf.format(combinations)}`;
  $('#hero-probability').textContent = pct(1 / combinations, 8);
  $('#hero-any-prize').textContent = fmtOdds(anyPrize);
  $('#hero-probability-bar').value = 1;
  $('#metric-draws').textContent = nf.format(stats.dataset?.drawCount || 0);
  $('#metric-range').textContent = stats.dataset?.firstDraw && stats.dataset?.lastDraw
    ? `${stats.dataset.firstDraw} → ${stats.dataset.lastDraw}` : 'Date range unavailable';
  $('#metric-latest').textContent = stats.dataset?.lastDraw || '—';
  $('#metric-entropy').textContent = Number(stats.fairnessDiagnostics?.normalizedEntropy || 0).toFixed(4);
  $('#metric-z').textContent = Number(stats.fairnessDiagnostics?.maxAbsoluteZScore || 0).toFixed(2);
  const latest = stats.dataset?.lastDraw ? new Date(`${stats.dataset.lastDraw}T00:00:00`) : null;
  const days = latest ? Math.floor((Date.now() - latest.getTime()) / 86_400_000) : Infinity;
  $('#metric-freshness').textContent = Number.isFinite(days)
    ? `${days} day${days === 1 ? '' : 's'} since dataset draw` : 'No validated date';
  const status = $('#header-data-status');
  status.classList.remove('is-skeleton', 'is-info', 'is-warning', 'is-danger');
  if (stats.legacyWarning) {
    status.classList.add('is-danger', 'is-light');
    status.textContent = 'Legacy data asset';
  } else if (days > 14) {
    status.classList.add('is-warning', 'is-light');
    status.textContent = 'Historical / stale';
  } else {
    status.classList.add('is-info', 'is-light');
    status.textContent = 'Validated data';
  }
}

function renderPlanner() {
  const stats = state.stats;
  const rows = stats.probabilityModel?.prizeDivisions?.length
    ? stats.probabilityModel.prizeDivisions : exactPrizeRows();
  const matches = stats.probabilityModel?.mainMatchDistribution?.length
    ? stats.probabilityModel.mainMatchDistribution : exactMatchRows();
  $('#prize-table-body').innerHTML = rows.map(row => `
    <tr><td>Division ${row.division}</td><td>${row.requirement}</td><td class="is-hidden-mobile">${pct(Number(row.probability), 6)}</td><td>${fmtOdds(Number(row.probability))}</td></tr>
  `).join('');
  const max = Math.max(...matches.map(row => Number(row.probability) || 0), 1e-12);
  $('#match-bars').innerHTML = `<div class="table-container"><table class="table is-fullwidth is-hoverable"><thead><tr><th>Matches</th><th>Probability</th><th>Relative frequency</th></tr></thead><tbody>${matches.map(row => `
    <tr><td><span class="tag is-rounded">${row.matches}</span></td><td>${pct(row.probability, 5)}</td><td><progress class="progress is-primary is-small" value="${row.probability}" max="${max}">${pct(row.probability, 5)}</progress></td></tr>
  `).join('')}</tbody></table></div>`;
  const update = () => {
    const games = Math.max(1, Math.min(200, Number($('#planner-games').value) || 1));
    const draws = Math.max(1, Math.min(520, Number($('#planner-draws').value) || 1));
    const perDraw = games / DIV1_COMBINATIONS;
    const cumulative = 1 - (1 - perDraw) ** draws;
    const system = Number($('#system-size').value);
    const combinations = comb(system, 6);
    $('#planner-games').value = games;
    $('#planner-draws').value = draws;
    $('#planner-games-output').value = games;
    $('#planner-games-output').textContent = games;
    $('#planner-draws-output').value = draws;
    $('#planner-draws-output').textContent = draws;
    $('#planner-per-draw').textContent = pct(perDraw, 8);
    $('#planner-per-draw-odds').textContent = fmtOdds(perDraw);
    $('#planner-cumulative').textContent = pct(cumulative, 8);
    $('#planner-cumulative-odds').textContent = fmtOdds(cumulative);
    $('#system-label').textContent = `System ${system} contains`;
    $('#system-combinations').textContent = nf.format(combinations);
  };
  ['#planner-games', '#planner-draws', '#system-size'].forEach(id => $(id).addEventListener('input', update));
  update();
}

function cryptoIndex(max) {
  if (globalThis.crypto?.getRandomValues) {
    const limit = 0x100000000 - (0x100000000 % max);
    const array = new Uint32Array(1);
    do crypto.getRandomValues(array); while (array[0] >= limit);
    return array[0] % max;
  }
  return Math.floor(Math.random() * max);
}
function shuffle(values) {
  const result = [...values];
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = cryptoIndex(i + 1);
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
function randomTicket() {
  return shuffle(Array.from({ length: BALL_COUNT }, (_, i) => i + 1)).slice(0, 6).sort((a, b) => a - b);
}
function randomTickets(count) {
  const output = [];
  const seen = new Set();
  while (output.length < count) {
    const ticket = randomTicket();
    const key = ticket.join(',');
    if (!seen.has(key)) { seen.add(key); output.push(ticket); }
  }
  return output;
}
function subsetKeys(ticket, size) {
  const output = [];
  function visit(start, selected) {
    if (selected.length === size) { output.push(selected.join(':')); return; }
    for (let i = start; i < ticket.length; i += 1) visit(i + 1, [...selected, ticket[i]]);
  }
  visit(0, []);
  return output;
}
function coverageTickets(count) {
  const tickets = [];
  const seen = new Set();
  const usage = new Map(Array.from({ length: 45 }, (_, i) => [i + 1, 0]));
  const covered = { 2: new Set(), 3: new Set(), 4: new Set() };
  for (let n = 0; n < count; n += 1) {
    let best = null;
    let bestScore = null;
    for (let candidateIndex = 0; candidateIndex < 180; candidateIndex += 1) {
      const candidate = randomTicket();
      const key = candidate.join(',');
      if (seen.has(key)) continue;
      const score = [4, 3, 2].map(size => subsetKeys(candidate, size).filter(value => !covered[size].has(value)).length);
      const maxOverlap = Math.max(0, ...tickets.map(ticket => ticket.filter(value => candidate.includes(value)).length));
      const usageCost = candidate.reduce((sum, value) => sum + usage.get(value), 0);
      const full = [...score, -maxOverlap, -usageCost, Math.random()];
      if (!bestScore || full.some((value, i) => value !== bestScore[i] && value > bestScore[i] && !full.slice(0, i).some((x, j) => x !== bestScore[j]))) {
        best = candidate;
        bestScore = full;
      }
    }
    if (!best) best = randomTicket();
    tickets.push(best);
    seen.add(best.join(','));
    best.forEach(value => usage.set(value, usage.get(value) + 1));
    [2, 3, 4].forEach(size => subsetKeys(best, size).forEach(key => covered[size].add(key)));
  }
  return tickets;
}
function crowdPenalty(ticket) {
  const sorted = [...ticket].sort((a, b) => a - b);
  const birthday = sorted.filter(number => number <= 31).length;
  const gaps = sorted.slice(1).map((number, i) => number - sorted[i]);
  const consecutive = gaps.filter(gap => gap === 1).length;
  const mean = gaps.reduce((a, b) => a + b, 0) / gaps.length;
  const variance = gaps.reduce((sum, gap) => sum + (gap - mean) ** 2, 0) / gaps.length;
  return birthday + (ticket.includes(7) ? 1.25 : 0) + 1.5 * consecutive + (variance <= 2 ? 1.5 : 0) + (birthday === 6 ? 2 : 0);
}
function antiCrowdingTickets(count) {
  const pool = randomTickets(Math.max(900, count * 30));
  return pool.map(ticket => ({ ticket, penalty: crowdPenalty(ticket), random: Math.random() }))
    .sort((a, b) => a.penalty - b.penalty || a.random - b.random)
    .slice(0, count).map(row => row.ticket);
}
function coverageMetric(tickets, size) {
  const unique = new Set(tickets.flatMap(ticket => subsetKeys(ticket, size))).size;
  const placements = tickets.length * comb(6, size);
  return { unique, placements, efficiency: placements ? unique / placements : 0, universe: unique / comb(45, size) };
}
function ticketMetrics(tickets) {
  const unique = new Set(tickets.flat()).size;
  let overlap = 0;
  for (let i = 0; i < tickets.length; i += 1) {
    for (let j = i + 1; j < tickets.length; j += 1) {
      overlap = Math.max(overlap, tickets[i].filter(number => tickets[j].includes(number)).length);
    }
  }
  return {
    unique,
    overlap,
    pair: coverageMetric(tickets, 2),
    triple: coverageMetric(tickets, 3),
    quad: coverageMetric(tickets, 4),
    div1: tickets.length / DIV1_COMBINATIONS,
  };
}
function prizeDivision(ticket, main, supplementary) {
  const mainMatches = ticket.filter(number => main.has(number)).length;
  const suppMatches = ticket.filter(number => supplementary.has(number)).length;
  if (mainMatches === 6) return 1;
  if (mainMatches === 5 && suppMatches) return 2;
  if (mainMatches === 5) return 3;
  if (mainMatches === 4) return 4;
  if (mainMatches === 3 && suppMatches) return 5;
  if (mainMatches === 3) return 6;
  return 0;
}
function sampleDraw() {
  const values = shuffle(Array.from({ length: 45 }, (_, i) => i + 1)).slice(0, 8);
  return { main: new Set(values.slice(0, 6)), supp: new Set(values.slice(6)) };
}
function wilson(successes, trials, z = 1.96) {
  if (!trials) return [0, 0];
  const probability = successes / trials;
  const denominator = 1 + z * z / trials;
  const center = (probability + z * z / (2 * trials)) / denominator;
  const margin = z * Math.sqrt((probability * (1 - probability) + z * z / (4 * trials)) / trials) / denominator;
  return [Math.max(0, center - margin), Math.min(1, center + margin)];
}
function simulatePortfolio(tickets, trials = 4000) {
  let hits = 0;
  for (let i = 0; i < trials; i += 1) {
    const draw = sampleDraw();
    if (tickets.some(ticket => prizeDivision(ticket, draw.main, draw.supp) > 0)) hits += 1;
  }
  return { probability: hits / trials, ci: wilson(hits, trials), trials };
}
function renderTickets(tickets) {
  state.tickets = tickets;
  const metrics = ticketMetrics(tickets);
  $('#coverage-unique').textContent = `${metrics.unique} / 45`;
  $('#coverage-overlap').textContent = `${metrics.overlap}`;
  $('#coverage-triples').textContent = pct(metrics.triple.efficiency, 1);
  $('#coverage-quads').textContent = pct(metrics.quad.efficiency, 1);
  $('#coverage-probability').textContent = pct(metrics.div1, 8);
  [['pair', metrics.pair], ['triple', metrics.triple], ['quad', metrics.quad]].forEach(([name, value]) => {
    $(`#${name}-coverage-label`).textContent = `${nf.format(value.unique)} / ${nf.format(value.placements)}`;
    $(`#${name}-coverage-meter`).value = 100 * value.efficiency;
  });
  $('#ticket-grid').innerHTML = tickets.map((ticket, i) => `
    <div class="column is-half py-2">
      <article class="box p-4">
        <div class="level is-mobile"><div class="level-left"><span class="tag is-primary is-light"><span class="icon"><i data-lucide="ticket"></i></span><span>Game ${String(i + 1).padStart(2, '0')}</span></span></div></div>
        <div class="tags are-medium">${ticket.map(number => `<span class="tag is-rounded is-primary">${number}</span>`).join('')}</div>
      </article>
    </div>
  `).join('');
  window.refreshIcons?.();
  $('#coverage-any-prize').textContent = 'Calculating…';
  $('#coverage-any-prize').classList.add('is-skeleton');
  $('#coverage-any-prize-ci').textContent = 'simulating';
  setTimeout(() => {
    const simulation = simulatePortfolio(tickets, Math.min(6000, 2500 + tickets.length * 100));
    $('#coverage-any-prize').classList.remove('is-skeleton');
    $('#coverage-any-prize').textContent = pct(simulation.probability, 2);
    $('#coverage-any-prize-ci').textContent = `95% CI ${pct(simulation.ci[0], 2)}–${pct(simulation.ci[1], 2)} · ${nf.format(simulation.trials)} draws`;
  }, 20);
}
function setupTicketLab() {
  const count = $('#ticket-count');
  const output = $('#ticket-count-output');
  function generate() {
    const number = Math.max(1, Math.min(40, Number(count.value) || 10));
    count.value = number;
    output.value = number;
    output.textContent = number;
    const mode = $('input[name="mode"]:checked').value;
    const tickets = mode === 'coverage' ? coverageTickets(number)
      : mode === 'anti-crowding' ? antiCrowdingTickets(number) : randomTickets(number);
    renderTickets(tickets);
    $('#mode-disclaimer').textContent = mode === 'anti-crowding'
      ? 'Experimental: selection patterns may affect prize sharing if a combination wins. They do not change draw probability.'
      : 'Portfolio structure changes overlap; every individual six-number combination keeps the same draw probability.';
    syncHash(mode, number, tickets);
  }
  count.addEventListener('input', () => { output.value = count.value; output.textContent = count.value; });
  $('#generate-tickets').addEventListener('click', generate);
  $$('input[name="mode"]').forEach(radio => radio.addEventListener('change', generate));
  $('#download-tickets').addEventListener('click', () => downloadText(
    'saturday-lotto-portfolio.csv',
    `game,n1,n2,n3,n4,n5,n6\n${state.tickets.map((ticket, i) => [i + 1, ...ticket].join(',')).join('\n')}\n`,
    'text/csv',
  ));
  $('#copy-share').addEventListener('click', async () => {
    syncHash($('input[name="mode"]:checked').value, Number(count.value), state.tickets);
    try { await navigator.clipboard.writeText(location.href); toast('Share link copied'); }
    catch { toast('Share URL is in the address bar'); }
  });
  const restored = restoreHash();
  if (restored) {
    count.value = restored.tickets.length;
    output.textContent = count.value;
    const radio = $(`input[name="mode"][value="${restored.mode}"]`);
    if (radio) radio.checked = true;
    renderTickets(restored.tickets);
  } else generate();
}
function syncHash(mode, count, tickets) {
  const compact = tickets.map(ticket => ticket.join('.')).join('-');
  history.replaceState(null, '', `#portfolio=${encodeURIComponent(mode)}:${count}:${compact}`);
}
function restoreHash() {
  const match = location.hash.match(/^#portfolio=([^:]+):(\d+):(.+)$/);
  if (!match) return null;
  try {
    const tickets = decodeURIComponent(match[3]).split('-').map(value => value.split('.').map(Number))
      .filter(ticket => ticket.length === 6 && new Set(ticket).size === 6 && ticket.every(number => number >= 1 && number <= 45));
    return tickets.length ? { mode: decodeURIComponent(match[1]), tickets } : null;
  } catch { return null; }
}
function downloadText(name, text, type = 'text/plain') {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 500);
}

function renderEvidence() {
  const simulation = state.stats.referenceSimulation;
  const backtest = state.stats.referenceBacktest;
  if (simulation) {
    const coverage = simulation.coverage?.simulation?.anyPrize;
    const random = simulation.random?.simulation?.anyPrize;
    const max = Math.max(coverage?.probability || 0, random?.probability || 0, 0.001);
    $('#sim-trials').textContent = `${nf.format(simulation.coverage?.simulation?.trials || 0)} trials`;
    $('#sim-coverage-any').textContent = pct(coverage?.probability, 2);
    $('#sim-random-any').textContent = pct(random?.probability, 2);
    $('#sim-coverage-bar').value = 100 * (coverage?.probability || 0) / max;
    $('#sim-random-bar').value = 100 * (random?.probability || 0) / max;
    $('#sim-coverage-ci').textContent = coverage?.ci95 ? `95% CI ${pct(coverage.ci95[0], 2)}–${pct(coverage.ci95[1], 2)}` : '—';
    $('#sim-random-ci').textContent = random?.ci95 ? `95% CI ${pct(random.ci95[0], 2)}–${pct(random.ci95[1], 2)}` : '—';
  } else {
    $('#sim-trials').textContent = 'Pending stats';
    $('#sim-coverage-any').textContent = '—';
    $('#sim-random-any').textContent = '—';
    $('#sim-coverage-ci').textContent = 'Reference simulation appears after the next statistics rebuild';
    $('#sim-random-ci').textContent = 'Reference simulation appears after the next statistics rebuild';
  }
  if (backtest) {
    $('#backtest-steps').textContent = `${backtest.steps} draws`;
    $('#backtest-table').innerHTML = `<div class="table-container"><table class="table is-fullwidth is-striped"><thead><tr><th>Measure</th><th>Coverage</th><th>QuickPick</th></tr></thead><tbody>
      <tr><td>Any prize</td><td>${pct(backtest.coverage?.anyPrizeRate, 1)}</td><td>${pct(backtest.random?.anyPrizeRate, 1)}</td></tr>
      <tr><td>Div 4 or better</td><td>${pct(backtest.coverage?.division4OrBetterRate, 2)}</td><td>${pct(backtest.random?.division4OrBetterRate, 2)}</td></tr>
      <tr><td>≥3 main</td><td>${pct(backtest.coverage?.atLeast3Rate, 1)}</td><td>${pct(backtest.random?.atLeast3Rate, 1)}</td></tr>
      <tr><td>Triple efficiency</td><td>${pct(backtest.coverage?.meanTripleCoverageEfficiency, 1)}</td><td>${pct(backtest.random?.meanTripleCoverageEfficiency, 1)}</td></tr>
    </tbody></table></div>`;
  } else {
    $('#backtest-steps').textContent = 'Pending stats';
    $('#backtest-table').innerHTML = '<div class="notification is-light">Walk-forward evidence appears after the statistics rebuild.</div>';
  }
}

function renderDrawExplorer() {
  const select = $('#draw-number');
  select.insertAdjacentHTML('beforeend', Array.from({ length: 45 }, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join(''));
  const draws = state.stats.draws || [];
  function apply(resetLimit = true) {
    if (resetLimit) state.drawLimit = 30;
    const query = $('#draw-search').value.trim().toLowerCase();
    const from = $('#draw-from').value;
    const to = $('#draw-to').value;
    const number = Number($('#draw-number').value) || null;
    state.filteredDraws = draws.filter(draw => {
      if (from && draw.date < from) return false;
      if (to && draw.date > to) return false;
      if (number && ![...(draw.main || []), ...(draw.supplementary || [])].includes(number)) return false;
      if (query) {
        const haystack = `${draw.date} ${(draw.main || []).join(' ')} ${(draw.supplementary || []).join(' ')}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });
    renderDrawRows();
  }
  function renderDrawRows() {
    const rows = state.filteredDraws.slice(0, state.drawLimit);
    $('#draw-result-count').textContent = nf.format(state.filteredDraws.length);
    $('#draw-list').innerHTML = rows.length ? rows.map(draw => `
      <article class="media box">
        <div class="media-left"><span class="icon"><i data-lucide="calendar-days"></i></span></div>
        <div class="media-content"><div class="content"><p><strong>${draw.date}</strong><br><small>Saturday Lotto · 6 main + 2 supplementary</small></p></div><div class="tags are-medium">${(draw.main || []).map(number => `<span class="tag is-primary is-rounded">${number}</span>`).join('')}${(draw.supplementary || []).map(number => `<span class="tag is-warning is-light is-rounded">${number}</span>`).join('')}</div></div>
      </article>
    `).join('') : '<div class="notification is-light">No matching draws in the currently loaded dataset.</div>';
    $('#load-more-draws').hidden = state.drawLimit >= state.filteredDraws.length;
    window.refreshIcons?.();
  }
  ['#draw-search', '#draw-from', '#draw-to', '#draw-number'].forEach(id => $(id).addEventListener('input', () => apply(true)));
  $('#reset-draw-filters').addEventListener('click', () => {
    $('#draw-search').value = '';
    $('#draw-from').value = '';
    $('#draw-to').value = '';
    $('#draw-number').value = '';
    apply(true);
  });
  $('#load-more-draws').addEventListener('click', () => { state.drawLimit += 30; renderDrawRows(); });
  $('#download-draws').addEventListener('click', () => {
    const csv = `date,main1,main2,main3,main4,main5,main6,supp1,supp2\n${state.filteredDraws.map(draw => [draw.date, ...draw.main, ...draw.supplementary].join(',')).join('\n')}\n`;
    downloadText('saturday-lotto-filtered-draws.csv', csv, 'text/csv');
  });
  apply(true);
}

function renderDiagnostics() {
  const stats = state.stats;
  const values = stats.numbers || [];
  const max = Math.max(1, ...values.map(row => Number(row.mainCount) || 0));
  $('#frequency-chart').innerHTML = `<div class="table-container"><table class="table is-fullwidth is-hoverable"><thead><tr><th>Number</th><th>Appearances</th><th class="is-hidden-mobile">Relative count</th><th>z-score</th></tr></thead><tbody>${values.map(row => `
    <tr><td><button class="button is-small is-light" type="button" data-frequency-number="${row.number}" aria-label="Number ${row.number}: ${row.mainCount || 0} appearances, z score ${Number(row.zScore || 0).toFixed(2)}">${row.number}</button></td><td>${nf.format(row.mainCount || 0)}</td><td class="is-hidden-mobile"><progress class="progress is-primary is-small" value="${row.mainCount || 0}" max="${max}">${row.mainCount || 0}</progress></td><td>${Number(row.zScore || 0).toFixed(2)}</td></tr>
  `).join('')}</tbody></table></div>`;
  $$('[data-frequency-number]').forEach(button => {
    const announce = () => { $('#chart-live').textContent = button.getAttribute('aria-label'); };
    button.addEventListener('focus', announce);
    button.addEventListener('click', announce);
  });
  const pairs = stats.topHistoricalPairs || [];
  $('#pair-grid').innerHTML = pairs.length ? pairs.slice(0, 16).map(row => `
    <div class="column is-one-quarter-desktop is-half-tablet"><article class="box"><div class="tags are-medium"><span class="tag is-primary is-rounded">${row.numbers[0]}</span><span class="tag is-primary is-rounded">${row.numbers[1]}</span></div><p><strong>${nf.format(row.count)} co-occurrences</strong></p><p class="help">${Number(row.liftVsExpected || 0).toFixed(2)}× expected historical count</p></article></div>
  `).join('') : '<div class="column"><div class="notification is-light">Pair diagnostics appear after the statistics rebuild.</div></div>';
  $('#quality-generated').textContent = stats.generatedAt ? new Date(stats.generatedAt).toLocaleString('en-AU') : '—';
  $('#quality-chi').textContent = Number(stats.fairnessDiagnostics?.chiSquareUniform || 0).toFixed(2);
  $('#quality-main').textContent = nf.format(stats.dataset?.mainObservations || 0);
  const provenance = state.provenance;
  const verification = provenance?.secondaryVerification;
  $('#quality-secondary').textContent = verification?.ok
    ? `${verification.verified}/${verification.requested} matched`
    : provenance?.status === 'bootstrap-placeholder' ? 'Awaiting rebuild' : 'Not recorded';
  $('#hash-winning').textContent = provenance?.files?.['winning_numbers.csv']?.sha256 || 'Awaiting rebuild';
  $('#hash-supp').textContent = provenance?.files?.['supplementary_numbers.csv']?.sha256 || 'Awaiting rebuild';
  const warning = $('#data-warning');
  const latest = stats.dataset?.lastDraw ? new Date(`${stats.dataset.lastDraw}T00:00:00`) : null;
  const days = latest ? Math.floor((Date.now() - latest.getTime()) / 86_400_000) : Infinity;
  if (stats.legacyWarning || days > 14 || provenance?.status === 'bootstrap-placeholder') {
    warning.hidden = false;
    warning.textContent = stats.legacyWarning
      ? 'This deployment is reading a legacy statistics asset. A verified refresh should replace it.'
      : days > 14 ? `Dataset is ${days} days behind the current date. Treat it as historical until a verified refresh succeeds.`
        : 'Provenance bootstrap record is present; rebuild statistics to generate CSV hashes.';
  } else warning.hidden = true;
}

function setupServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => navigator.serviceWorker.register('service-worker.js')
      .catch(error => console.warn('Service worker registration failed', error)));
  }
}
async function init() {
  setupTabs();
  setupTicketLab();
  setupServiceWorker();
  await loadData();
}
document.addEventListener('DOMContentLoaded', init);
