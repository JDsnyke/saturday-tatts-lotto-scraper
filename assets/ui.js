(() => {
  const THEME_KEY = 'lotto-theme';
  const RELOAD_KEY = 'lotto-sw-reloaded';
  const themes = ['system', 'light', 'dark'];
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  let resolvedTheme = 'light';

  function refreshIcons() {
    harmonizeTheme(document);
    if (window.lucide?.createIcons) window.lucide.createIcons();
  }

  function harmonizeTheme(root = document) {
    const scope = root instanceof Element ? root : document;
    const candidates = [];
    if (root instanceof Element && (root.classList.contains('is-light') || root.dataset.bulmaLightVariant === 'true')) {
      candidates.push(root);
    }
    scope.querySelectorAll?.('.is-light, [data-bulma-light-variant="true"]').forEach(element => candidates.push(element));
    [...new Set(candidates)].forEach(element => {
      element.dataset.bulmaLightVariant = 'true';
      element.classList.toggle('is-light', resolvedTheme !== 'dark');
    });
  }

  function applyTheme(theme) {
    const preference = themes.includes(theme) ? theme : 'system';
    resolvedTheme = preference === 'system' ? (media.matches ? 'dark' : 'light') : preference;
    document.documentElement.setAttribute('data-theme', resolvedTheme);
    document.documentElement.setAttribute('data-theme-preference', preference);
    localStorage.setItem(THEME_KEY, preference);

    const themeMeta = document.querySelector('meta[name="theme-color"]');
    if (themeMeta) themeMeta.content = resolvedTheme === 'dark' ? '#14161a' : '#ffffff';

    const button = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    if (button) {
      const label = preference === 'system' ? `System (${resolvedTheme})` : preference[0].toUpperCase() + preference.slice(1);
      button.setAttribute('aria-label', `Theme: ${label}. Activate to change theme.`);
      button.title = `Theme: ${label}`;
    }
    if (icon) icon.setAttribute('data-lucide', preference === 'dark' ? 'moon' : preference === 'light' ? 'sun' : 'monitor');
    harmonizeTheme(document);
    if (window.lucide?.createIcons) window.lucide.createIcons();
  }

  function setupTheme() {
    applyTheme(localStorage.getItem(THEME_KEY) || 'system');
    media.addEventListener('change', () => {
      if ((localStorage.getItem(THEME_KEY) || 'system') === 'system') applyTheme('system');
    });
    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      const current = localStorage.getItem(THEME_KEY) || 'system';
      applyTheme(themes[(themes.indexOf(current) + 1) % themes.length]);
    });

    const observer = new MutationObserver(records => {
      records.forEach(record => record.addedNodes.forEach(node => {
        if (node instanceof Element) harmonizeTheme(node);
      }));
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function setupNavbars() {
    document.querySelectorAll('.navbar-burger').forEach(burger => {
      burger.addEventListener('click', () => {
        const target = document.getElementById(burger.dataset.target);
        const active = !burger.classList.contains('is-active');
        burger.classList.toggle('is-active', active);
        burger.setAttribute('aria-expanded', String(active));
        target?.classList.toggle('is-active', active);
      });
    });
  }

  function clearSkeletons(root = document) {
    root.querySelectorAll('.is-skeleton, .has-skeleton').forEach(element => element.classList.remove('is-skeleton', 'has-skeleton'));
    root.querySelectorAll('.skeleton-block, .skeleton-lines').forEach(element => element.remove());
  }

  function setupServiceWorker() {
    if (!('serviceWorker' in navigator)) return;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (sessionStorage.getItem(RELOAD_KEY) === 'true') return;
      sessionStorage.setItem(RELOAD_KEY, 'true');
      location.reload();
    });
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('./service-worker.js');
        await registration.update();
      } catch (error) {
        console.warn('Service worker registration failed', error);
      }
    });
  }

  window.refreshIcons = refreshIcons;
  window.clearSkeletons = clearSkeletons;
  window.applyLotteryTheme = applyTheme;

  function setup() {
    setupTheme();
    setupNavbars();
    setupServiceWorker();
    refreshIcons();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup);
  else setup();
})();
