import fs from 'node:fs/promises';
import { chromium } from 'playwright';

const base = process.env.AUDIT_BASE || 'https://jdsnyke.github.io/saturday-tatts-lotto-scraper/';
const pages = [
  ['saturday', ''],
  ['games', 'games.html'],
  ['benchmarks', 'benchmark.html'],
];
const viewports = {
  desktop: { width: 1440, height: 1000 },
  mobile: { width: 390, height: 844 },
};
const themes = ['light', 'dark'];

await fs.mkdir('browser-audit', { recursive: true });
const browser = await chromium.launch({ headless: true });
const report = [];

for (const [pageName, path] of pages) {
  for (const [viewportName, viewport] of Object.entries(viewports)) {
    for (const theme of themes) {
      const consoleErrors = [];
      const requestFailures = [];
      const context = await browser.newContext({ viewport, colorScheme: theme });
      await context.addInitScript(value => localStorage.setItem('lotto-theme', value), theme);
      const page = await context.newPage();
      page.on('console', message => {
        if (message.type() === 'error') consoleErrors.push(message.text());
      });
      page.on('requestfailed', request => requestFailures.push({
        url: request.url(),
        error: request.failure()?.errorText || 'unknown',
      }));

      const url = new URL(path, base).href;
      let navigationError = null;
      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 60_000 });
      } catch (error) {
        navigationError = String(error);
      }
      await page.waitForTimeout(1500);

      if (viewportName === 'mobile') {
        const burger = page.locator('.navbar-burger');
        if (await burger.count()) {
          await burger.click();
          await page.waitForTimeout(200);
        }
      }

      const metrics = await page.evaluate(({ pageName, viewportName, theme }) => {
        const visible = element => {
          const style = getComputedStyle(element);
          const rect = element.getBoundingClientRect();
          return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) !== 0 && rect.width > 0 && rect.height > 0;
        };
        const rgba = value => {
          const match = value?.match(/rgba?\(([^)]+)\)/);
          if (!match) return null;
          const values = match[1].split(',').map(part => Number.parseFloat(part.trim()));
          return { r: values[0], g: values[1], b: values[2], a: values.length > 3 ? values[3] : 1 };
        };
        const backgroundFor = element => {
          let current = element;
          while (current) {
            const parsed = rgba(getComputedStyle(current).backgroundColor);
            if (parsed && parsed.a > 0.01) return parsed;
            current = current.parentElement;
          }
          return theme === 'dark' ? { r: 20, g: 22, b: 26, a: 1 } : { r: 255, g: 255, b: 255, a: 1 };
        };
        const luminance = colour => {
          const channel = value => {
            const scaled = value / 255;
            return scaled <= 0.03928 ? scaled / 12.92 : ((scaled + 0.055) / 1.055) ** 2.4;
          };
          return 0.2126 * channel(colour.r) + 0.7152 * channel(colour.g) + 0.0722 * channel(colour.b);
        };
        const contrast = (a, b) => {
          const x = luminance(a);
          const y = luminance(b);
          return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
        };

        const overflow = [...document.querySelectorAll('body *')]
          .map(element => ({ element, rect: element.getBoundingClientRect() }))
          .filter(({ element, rect }) => visible(element) && (rect.right > innerWidth + 1 || rect.left < -1 || rect.width > innerWidth + 1))
          .slice(0, 40)
          .map(({ element, rect }) => ({
            tag: element.tagName.toLowerCase(),
            id: element.id || null,
            className: typeof element.className === 'string' ? element.className : null,
            text: (element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 120),
            left: Math.round(rect.left), right: Math.round(rect.right), width: Math.round(rect.width),
          }));

        const skeletons = [...document.querySelectorAll('.is-skeleton,.has-skeleton,.skeleton-lines,.skeleton-block')]
          .filter(visible)
          .map(element => ({ id: element.id || null, className: element.className, text: (element.textContent || '').trim().slice(0, 100) }));

        const lowContrast = [];
        if (theme === 'dark') {
          const selectors = '.title,.subtitle,.label,.heading,.navbar-item,.button,.notification,.message-body,.box p,.card p,.table th,.table td';
          [...document.querySelectorAll(selectors)].filter(visible).forEach(element => {
            const text = (element.textContent || '').trim().replace(/\s+/g, ' ');
            if (!text || text.length > 500) return;
            const foreground = rgba(getComputedStyle(element).color);
            if (!foreground) return;
            const ratio = contrast(foreground, backgroundFor(element));
            if (ratio < 3) lowContrast.push({
              tag: element.tagName.toLowerCase(),
              id: element.id || null,
              className: element.className,
              text: text.slice(0, 100),
              ratio: Number(ratio.toFixed(2)),
            });
          });
        }

        const shadowedSurfaces = [...document.querySelectorAll('.box,.card')]
          .filter(visible)
          .filter(element => getComputedStyle(element).boxShadow !== 'none')
          .slice(0, 20)
          .map(element => ({ tag: element.tagName.toLowerCase(), id: element.id || null, className: element.className }));

        const menuRects = viewportName === 'mobile'
          ? [...document.querySelectorAll('.navbar-menu.is-active .navbar-item')].filter(visible).map(element => {
              const rect = element.getBoundingClientRect();
              return { text: (element.textContent || '').trim().replace(/\s+/g, ' '), top: rect.top, bottom: rect.bottom, height: rect.height };
            })
          : [];
        const menuOverlap = menuRects.some((row, index) => index > 0 && row.top < menuRects[index - 1].bottom - 1);
        const menuTooShort = menuRects.some(row => row.height < 36);

        const bodyText = document.body.innerText.toLowerCase();
        const localBulma = [...document.styleSheets].some(sheet => String(sheet.href || '').includes('/assets/vendor/bulma.min.css'));
        const localLucide = typeof window.lucide?.createIcons === 'function';
        const statusId = pageName === 'games' ? 'catalog-status' : 'header-data-status';
        const statusText = (document.getElementById(statusId)?.textContent || '').trim();

        const loaded = (() => {
          if (pageName === 'saturday') {
            const drawCount = Number((document.getElementById('metric-draws')?.textContent || '').replace(/[^0-9]/g, ''));
            const resultCount = Number((document.getElementById('draw-result-count')?.textContent || '').replace(/[^0-9]/g, ''));
            const frequencyRows = document.querySelectorAll('#frequency-chart tbody tr').length;
            const drawRows = document.querySelectorAll('#draw-list article.media').length;
            const backtestReady = !document.querySelector('#backtest-table .skeleton-lines');
            return { ok: drawCount > 0 && resultCount > 0 && frequencyRows > 0 && drawRows > 0 && backtestReady, drawCount, resultCount, frequencyRows, drawRows, backtestReady };
          }
          if (pageName === 'games') {
            const gameCards = document.querySelectorAll('#game-grid [data-game]').length;
            return { ok: gameCards > 0 && !/loading|unavailable/i.test(statusText), gameCards };
          }
          const certificateValues = ['cert-any-exact', 'cert-any-lower', 'cert-d4-exact', 'cert-overlap'].map(id => document.getElementById(id)?.textContent?.trim() || '');
          const referenceReady = !document.querySelector('#benchmark-reference .skeleton-lines');
          return { ok: certificateValues.every(value => value && !/loading|checking|^0{2}\.0/i.test(value)) && referenceReady, certificateValues, referenceReady };
        })();

        return {
          title: document.title,
          dataTheme: document.documentElement.getAttribute('data-theme'),
          themePreference: document.documentElement.getAttribute('data-theme-preference'),
          innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          bodyScrollWidth: document.body.scrollWidth,
          overflow,
          skeletons,
          skeletonCount: skeletons.length,
          lowContrast: lowContrast.slice(0, 30),
          shadowedSurfaces,
          menuItemCount: menuRects.length,
          menuOverlap,
          menuTooShort,
          localBulma,
          localLucide,
          visibleLegacyText: bodyText.includes('legacy data') || bodyText.includes('legacy statistics'),
          statusText,
          loaded,
        };
      }, { pageName, viewportName, theme });

      const filename = `browser-audit/${pageName}-${viewportName}-${theme}.png`;
      await page.screenshot({ path: filename, fullPage: true });
      report.push({ page: pageName, viewport: viewportName, theme, url, navigationError, consoleErrors, requestFailures, ...metrics });
      await context.close();
    }
  }
}

await browser.close();
await fs.writeFile('browser-audit/audit.json', JSON.stringify(report, null, 2));

const failures = [];
for (const row of report) {
  const label = `${row.page}/${row.viewport}/${row.theme}`;
  if (row.navigationError) failures.push(`${label}: navigation failed: ${row.navigationError}`);
  if (row.consoleErrors.length) failures.push(`${label}: ${row.consoleErrors.length} console error(s)`);
  if (row.requestFailures.length) failures.push(`${label}: ${row.requestFailures.length} request failure(s)`);
  if (!row.localBulma) failures.push(`${label}: local Bulma stylesheet did not load`);
  if (!row.localLucide) failures.push(`${label}: local Lucide runtime did not load`);
  if (row.skeletonCount) failures.push(`${label}: ${row.skeletonCount} visible skeleton(s) remain`);
  if (row.scrollWidth > row.innerWidth + 1) failures.push(`${label}: horizontal overflow ${row.scrollWidth}px > ${row.innerWidth}px`);
  if (row.dataTheme !== row.theme) failures.push(`${label}: theme mismatch (${row.dataTheme} != ${row.theme})`);
  if (row.lowContrast.length) failures.push(`${label}: ${row.lowContrast.length} sampled text element(s) below 3:1 contrast`);
  if (row.shadowedSurfaces.length) failures.push(`${label}: ${row.shadowedSurfaces.length} visible box/card surface(s) still have shadows`);
  if (row.viewport === 'mobile' && row.menuItemCount === 0) failures.push(`${label}: mobile menu did not open`);
  if (row.viewport === 'mobile' && row.menuOverlap) failures.push(`${label}: mobile navbar items overlap`);
  if (row.viewport === 'mobile' && row.menuTooShort) failures.push(`${label}: mobile navbar items are too tightly packed`);
  if (row.visibleLegacyText) failures.push(`${label}: legacy-data messaging is visible`);
  if (!row.loaded.ok) failures.push(`${label}: page-specific content did not finish loading (${JSON.stringify(row.loaded)})`);
}

if (failures.length) {
  console.error(`UI browser audit failed with ${failures.length} invariant violation(s):`);
  failures.forEach(message => console.error(`- ${message}`));
  process.exitCode = 1;
} else {
  console.log(`UI browser audit passed: ${report.length} page/viewport/theme combinations with contrast, data and mobile-menu checks.`);
}
