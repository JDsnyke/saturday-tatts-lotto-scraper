(() => {
  const THEME_KEY = 'lotto-theme';
  const themes = ['system', 'light', 'dark'];

  function refreshIcons(root = document) {
    if (!window.lucide?.createIcons) return;
    window.lucide.createIcons({ attrs: { 'aria-hidden': 'true' }, nameAttr: 'data-lucide' });
  }

  function applyTheme(theme) {
    const value = themes.includes(theme) ? theme : 'system';
    if (value === 'system') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', value);
    localStorage.setItem(THEME_KEY, value);

    const button = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    if (button) {
      button.setAttribute('aria-label', `Theme: ${value}. Activate to change theme.`);
      button.title = `Theme: ${value}`;
    }
    if (icon) {
      icon.setAttribute('data-lucide', value === 'dark' ? 'moon' : value === 'light' ? 'sun' : 'monitor');
    }
    refreshIcons();
  }

  function setupTheme() {
    applyTheme(localStorage.getItem(THEME_KEY) || 'system');
    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      const current = localStorage.getItem(THEME_KEY) || 'system';
      applyTheme(themes[(themes.indexOf(current) + 1) % themes.length]);
    });
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
    root.querySelectorAll('.is-skeleton').forEach(element => element.classList.remove('is-skeleton'));
    root.querySelectorAll('.skeleton-block, .skeleton-lines').forEach(element => element.remove());
  }

  window.refreshIcons = refreshIcons;
  window.clearSkeletons = clearSkeletons;

  function setup() {
    setupTheme();
    setupNavbars();
    refreshIcons();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup);
  else setup();
})();
