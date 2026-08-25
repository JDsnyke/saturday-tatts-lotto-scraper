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
      page.on('requestfailed', request => {
        requestFailures.push({ url: request.url(), error: request.failure()?.errorText || 'unknown' });
      });

      const url = new URL(path, base).href;
      let navigationError = null;
      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 60_000 });
      } catch (error) {
        navigationError = String(error);
      }
      await page.waitForTimeout(2500);

      const metrics = await page.evaluate(() => {
        const visible = element => {
          const style = getComputedStyle(element);
          const rect = element.getBoundingClientRect();
          return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
        };
        const overflow = [...document.querySelectorAll('body *')]
          .map(element => ({ element, rect: element.getBoundingClientRect() }))
          .filter(({ element, rect }) => visible(element) && (rect.right > innerWidth + 1 || rect.left < -1 || rect.width > innerWidth + 1))
          .slice(0, 40)
          .map(({ element, rect }) => ({
            tag: element.tagName.toLowerCase(),
            id: element.id || null,
            className: typeof element.className === 'string' ? element.className : null,
            text: (element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 140),
            left: Math.round(rect.left),
            right: Math.round(rect.right),
            width: Math.round(rect.width),
          }));
        const skeletons = [...document.querySelectorAll('.is-skeleton,.has-skeleton,.skeleton-lines,.skeleton-block')]
          .filter(visible)
          .map(element => ({
            tag: element.tagName.toLowerCase(),
            id: element.id || null,
            className: element.className,
            text: (element.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 140),
          }));
        const sample = selector => {
          const element = document.querySelector(selector);
          if (!element) return null;
          const style = getComputedStyle(element);
          return {
            backgroundColor: style.backgroundColor,
            color: style.color,
            padding: style.padding,
            margin: style.margin,
          };
        };
        return {
          title: document.title,
          readyState: document.readyState,
          dataTheme: document.documentElement.getAttribute('data-theme'),
          innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          bodyScrollWidth: document.body.scrollWidth,
          body: sample('body'),
          html: sample('html'),
          navbar: sample('.navbar'),
          hero: sample('.hero'),
          heroBox: sample('.hero .box'),
          heroBoxTitle: sample('.hero .box .title'),
          firstBox: sample('.box'),
          firstSection: sample('.section'),
          overflow,
          skeletons,
          skeletonCount: skeletons.length,
          navBurgerVisible: (() => {
            const element = document.querySelector('.navbar-burger');
            return element ? visible(element) : false;
          })(),
        };
      });

      const filename = `browser-audit/${pageName}-${viewportName}-${theme}.png`;
      await page.screenshot({ path: filename, fullPage: true });
      report.push({
        page: pageName,
        viewport: viewportName,
        theme,
        url,
        navigationError,
        consoleErrors,
        requestFailures,
        ...metrics,
      });
      await context.close();
    }
  }
}

await browser.close();
await fs.writeFile('browser-audit/audit.json', JSON.stringify(report, null, 2));
