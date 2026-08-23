(() => {
  const nf = new Intl.NumberFormat('en-AU');
  const pct = (value, digits = 2) => new Intl.NumberFormat('en-AU', {
    style: 'percent',
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Number(value) || 0);
  const $ = selector => document.querySelector(selector);

  const comb = (n, k) => {
    if (k < 0 || k > n) return 0;
    k = Math.min(k, n - k);
    let value = 1;
    for (let i = 1; i <= k; i += 1) value = (value * (n - k + i)) / i;
    return Math.round(value);
  };

  function mulberry32(seed) {
    let state = seed >>> 0;
    return () => {
      state += 0x6d2b79f5;
      let value = state;
      value = Math.imul(value ^ (value >>> 15), value | 1);
      value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
      return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
    };
  }

  function shuffle(values, rng) {
    const result = [...values];
    for (let i = result.length - 1; i > 0; i -= 1) {
      const j = Math.floor(rng() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  function randomTicket(rng) {
    return shuffle(Array.from({ length: 45 }, (_, index) => index + 1), rng)
      .slice(0, 6).sort((a, b) => a - b);
  }

  function randomPortfolio(count, rng) {
    const tickets = [];
    const seen = new Set();
    while (tickets.length < count) {
      const ticket = randomTicket(rng);
      const key = ticket.join(',');
      if (!seen.has(key)) { seen.add(key); tickets.push(ticket); }
    }
    return tickets;
  }

  function subsetKeys(ticket, size) {
    const keys = [];
    function visit(start, selected) {
      if (selected.length === size) { keys.push(selected.join(':')); return; }
      for (let index = start; index < ticket.length; index += 1) {
        visit(index + 1, [...selected, ticket[index]]);
      }
    }
    visit(0, []);
    return keys;
  }

  function coveragePortfolio(count, rng, candidatesPerTicket = 70) {
    const tickets = [];
    const seen = new Set();
    const usage = new Map(Array.from({ length: 45 }, (_, index) => [index + 1, 0]));
    const covered = { 2: new Set(), 3: new Set(), 4: new Set() };
    for (let game = 0; game < count; game += 1) {
      let best = null;
      let bestScore = null;
      for (let candidateIndex = 0; candidateIndex < candidatesPerTicket; candidateIndex += 1) {
        const candidate = randomTicket(rng);
        const key = candidate.join(',');
        if (seen.has(key)) continue;
        const new4 = subsetKeys(candidate, 4).filter(value => !covered[4].has(value)).length;
        const new3 = subsetKeys(candidate, 3).filter(value => !covered[3].has(value)).length;
        const new2 = subsetKeys(candidate, 2).filter(value => !covered[2].has(value)).length;
        const maxOverlap = Math.max(0, ...tickets.map(ticket => ticket.filter(value => candidate.includes(value)).length));
        const usageCost = candidate.reduce((total, value) => total + usage.get(value), 0);
        const score = [new4, new3, new2, -maxOverlap, -usageCost, rng()];
        if (!bestScore) { best = candidate; bestScore = score; continue; }
        for (let index = 0; index < score.length; index += 1) {
          if (score[index] === bestScore[index]) continue;
          if (score[index] > bestScore[index]) { best = candidate; bestScore = score; }
          break;
        }
      }
      if (!best) best = randomTicket(rng);
      tickets.push(best);
      seen.add(best.join(','));
      best.forEach(value => usage.set(value, usage.get(value) + 1));
      [2, 3, 4].forEach(size => subsetKeys(best, size).forEach(key => covered[size].add(key)));
    }
    return tickets;
  }

  function coverageEfficiency(tickets, size) {
    const unique = new Set(tickets.flatMap(ticket => subsetKeys(ticket, size))).size;
    return unique / (tickets.length * comb(6, size));
  }

  function sampleDraws(count, rng) {
    const population = Array.from({ length: 45 }, (_, index) => index + 1);
    return Array.from({ length: count }, () => new Set(shuffle(population, rng).slice(0, 6)));
  }

  function outcomeRates(tickets, draws) {
    const ticketSets = tickets.map(ticket => new Set(ticket));
    let anyPrize = 0;
    let division4OrBetter = 0;
    for (const draw of draws) {
      let best = 0;
      for (const ticket of ticketSets) {
        let matches = 0;
        ticket.forEach(value => { if (draw.has(value)) matches += 1; });
        if (matches > best) best = matches;
      }
      if (best >= 3) anyPrize += 1;
      if (best >= 4) division4OrBetter += 1;
    }
    return { anyPrizeRate: anyPrize / draws.length, division4OrBetterRate: division4OrBetter / draws.length };
  }

  function quantile(values, probability) {
    const ordered = [...values].sort((a, b) => a - b);
    if (ordered.length === 1) return ordered[0];
    const position = (ordered.length - 1) * probability;
    const lower = Math.floor(position);
    const upper = Math.min(lower + 1, ordered.length - 1);
    const fraction = position - lower;
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction;
  }

  function summary(values) {
    const mean = values.reduce((total, value) => total + value, 0) / values.length;
    return { mean, p05: quantile(values, 0.05), median: quantile(values, 0.5), p95: quantile(values, 0.95) };
  }

  function superiority(coverage, baseline, direction = 'higher') {
    let wins = 0;
    let total = 0;
    coverage.forEach(a => baseline.forEach(b => {
      total += 1;
      if (a === b) wins += 0.5;
      else if ((direction === 'higher' && a > b) || (direction === 'lower' && a < b)) wins += 1;
    }));
    return wins / total;
  }

  function metricRow(label, metric, digits = 2) {
    if (!metric) return '';
    const comparison = metric.comparison || {};
    const ci = comparison.bootstrapMeanDifferenceCi95;
    const format = value => pct(value, digits);
    return `<tr><td><strong>${label}</strong><br><small>${comparison.direction === 'lower' ? 'lower is better' : 'higher is better'}</small></td><td>${format(metric.coverage?.mean)}</td><td>${format(metric.random?.mean)}</td><td>${pct(comparison.probabilityOfSuperiority, 1)}</td><td>${ci ? `${format(ci[0])} → ${format(ci[1])}` : '—'}</td></tr>`;
  }

  function renderReference(benchmark) {
    const target = $('#benchmark-reference');
    if (!target) return;
    if (!benchmark?.metrics) {
      target.innerHTML = '<div class="notification is-light">Reference benchmark pending generated stats. Use the local benchmark below until the scheduled verified refresh publishes it.</div>';
      return;
    }
    const metrics = benchmark.metrics;
    target.innerHTML = `
      <div class="tags"><span class="tag">${nf.format(benchmark.coveragePortfolios)} coverage portfolios</span><span class="tag">${nf.format(benchmark.randomPortfolios)} QuickPick portfolios</span><span class="tag">${nf.format(benchmark.simulatedDraws)} shared draws</span><span class="tag">seed ${benchmark.seed}</span></div>
      <div class="table-container"><table class="table is-fullwidth is-striped is-hoverable"><thead><tr><th>Metric</th><th>Coverage mean</th><th>QuickPick mean</th><th>P(superior)</th><th>95% CI of favourable Δ</th></tr></thead><tbody>
        ${metricRow('Triple efficiency', metrics.tripleCoverageEfficiency, 2)}
        ${metricRow('Quad efficiency', metrics.quadCoverageEfficiency, 2)}
        ${metricRow('Any-prize rate', metrics.anyPrizeRate, 2)}
        ${metricRow('Div 4+ rate', metrics.division4OrBetterRate, 3)}
      </tbody></table></div>
      <div class="notification is-light">${benchmark.note || ''}</div>`;
    window.clearSkeletons?.(target);
  }

  async function loadReference() {
    try {
      const response = await fetch('assets/lotto_stats.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const stats = await response.json();
      renderReference(stats.referenceBenchmark);
    } catch (error) {
      console.warn('benchmark reference unavailable', error);
      renderReference(null);
    }
  }

  function setProgress(value) {
    const progress = $('#benchmark-progress');
    if (!progress) return;
    const clamped = Math.max(0, Math.min(1, value));
    progress.value = clamped * 100;
    progress.classList.toggle('is-hidden', clamped <= 0 || clamped >= 1);
  }

  function localMetric(label, coverageValues, randomValues, digits = 2) {
    return {
      label,
      coverage: summary(coverageValues),
      random: summary(randomValues),
      superiority: superiority(coverageValues, randomValues),
      digits,
    };
  }

  function renderLocal(result) {
    const target = $('#benchmark-local-result');
    const rows = result.metrics.map(metric => `<tr><td><strong>${metric.label}</strong><br><small>local exploratory run</small></td><td>${pct(metric.coverage.mean, metric.digits)}</td><td>${pct(metric.random.mean, metric.digits)}</td><td>${pct(metric.superiority, 1)}</td><td>${pct(metric.coverage.p05, metric.digits)}–${pct(metric.coverage.p95, metric.digits)}</td></tr>`).join('');
    target.innerHTML = `
      <div class="tags"><span class="tag">${result.coveragePortfolios} coverage</span><span class="tag">${result.randomPortfolios} QuickPick</span><span class="tag">${nf.format(result.draws)} shared draws</span><span class="tag">seed ${result.seed}</span></div>
      <div class="table-container"><table class="table is-fullwidth is-striped"><thead><tr><th>Metric</th><th>Coverage mean</th><th>QuickPick mean</th><th>P(superior)</th><th>Coverage 5–95%</th></tr></thead><tbody>${rows}</tbody></table></div>
      <div class="notification is-warning is-light">Local results are exploratory and smaller than the precomputed repository benchmark. Same-sized distinct portfolios retain identical Division 1 probability.</div>`;
  }

  async function runLocal() {
    const button = $('#run-local-benchmark');
    const download = $('#download-local-benchmark');
    const games = Math.max(2, Math.min(20, Number($('#bench-games').value) || 10));
    const coverageCount = Math.max(2, Math.min(24, Number($('#bench-coverage').value) || 8));
    const randomCount = Math.max(4, Math.min(80, Number($('#bench-random').value) || 32));
    const trials = Math.max(300, Math.min(2500, Number($('#bench-trials').value) || 1000));
    const seed = Number($('#bench-seed').value) || 20260822;
    button.disabled = true;
    button.classList.add('is-loading');
    download.disabled = true;
    $('#benchmark-local-result').innerHTML = '<div class="notification is-light is-skeleton">Generating independently seeded portfolios…</div>';
    setProgress(0.05);
    await new Promise(resolve => setTimeout(resolve, 20));

    const drawRng = mulberry32((seed ^ 0x5a172026) >>> 0);
    const draws = sampleDraws(trials, drawRng);
    const coverageRows = [];
    const randomRows = [];
    for (let index = 0; index < coverageCount; index += 1) {
      const rng = mulberry32((seed + 10007 * (index + 1)) >>> 0);
      const tickets = coveragePortfolio(games, rng);
      const outcomes = outcomeRates(tickets, draws);
      coverageRows.push({ triple: coverageEfficiency(tickets, 3), quad: coverageEfficiency(tickets, 4), ...outcomes });
      setProgress(0.05 + 0.4 * ((index + 1) / coverageCount));
      if (index % 2 === 1) await new Promise(resolve => setTimeout(resolve, 0));
    }
    for (let index = 0; index < randomCount; index += 1) {
      const rng = mulberry32((seed + 70001 + 20011 * (index + 1)) >>> 0);
      const tickets = randomPortfolio(games, rng);
      const outcomes = outcomeRates(tickets, draws);
      randomRows.push({ triple: coverageEfficiency(tickets, 3), quad: coverageEfficiency(tickets, 4), ...outcomes });
      setProgress(0.45 + 0.5 * ((index + 1) / randomCount));
      if (index % 4 === 3) await new Promise(resolve => setTimeout(resolve, 0));
    }

    const result = {
      games,
      coveragePortfolios: coverageCount,
      randomPortfolios: randomCount,
      draws: trials,
      seed,
      divisionOneProbabilityEqual: true,
      metrics: [
        localMetric('Triple efficiency', coverageRows.map(row => row.triple), randomRows.map(row => row.triple)),
        localMetric('Quad efficiency', coverageRows.map(row => row.quad), randomRows.map(row => row.quad)),
        localMetric('Any-prize rate', coverageRows.map(row => row.anyPrizeRate), randomRows.map(row => row.anyPrizeRate)),
        localMetric('Div 4+ rate', coverageRows.map(row => row.division4OrBetterRate), randomRows.map(row => row.division4OrBetterRate), 3),
      ],
    };
    window.__lottoLocalBenchmark = result;
    setProgress(1);
    renderLocal(result);
    button.disabled = false;
    button.classList.remove('is-loading');
    download.disabled = false;
  }

  function downloadLocal() {
    const result = window.__lottoLocalBenchmark;
    if (!result) return;
    const blob = new Blob([`${JSON.stringify(result, null, 2)}\n`], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'saturday-lotto-local-benchmark.json';
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 500);
  }

  function setup() {
    loadReference();
    $('#run-local-benchmark')?.addEventListener('click', runLocal);
    $('#download-local-benchmark')?.addEventListener('click', downloadLocal);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup);
  else setup();
})();
