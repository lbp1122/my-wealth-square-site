(() => {
  // MWS supplies its own translations. A second browser translation can mix
  // languages and corrupt names when these DOM nodes change dynamically.
  const languageNames = {
    en: 'English', bm: 'Bahasa Melayu', zh: '简体中文', 'zh-TW': '繁體中文',
    th: 'ไทย', ja: '日本語', ko: '한국어', vi: 'Tiếng Việt',
  };
  const validLanguage = lang => Object.hasOwn(languageNames, lang);
  const select = document.getElementById('language');
  document.documentElement.setAttribute('translate', 'no');
  document.documentElement.classList.add('notranslate');

  function setLang(lang) {
    if (!validLanguage(lang)) lang = 'en';
    const selected = copy[lang];
    document.documentElement.lang = {bm: 'ms', zh: 'zh-CN'}[lang] || lang;
    document.querySelectorAll('[data-k]').forEach(el => {
      const value = selected[el.dataset.k];
      if (value !== undefined) el.textContent = value;
    });
    document.querySelectorAll('[data-k-html]').forEach(el => {
      const value = selected[el.dataset.kHtml];
      if (value !== undefined) el.innerHTML = value;
    });
    if (select) {
      select.setAttribute('translate', 'no');
      select.classList.add('notranslate');
      Array.from(select.options).forEach(option => {
        option.textContent = languageNames[option.value];
        option.setAttribute('translate', 'no');
      });
      select.value = lang;
    }
    document.querySelectorAll('.brand span, .visual-heading span, footer strong, .back-link.home-link')
      .forEach(el => {
        el.textContent = 'My Wealth Square';
        el.setAttribute('translate', 'no');
      });
    try { localStorage.setItem('mws-review-lang', lang); } catch (_) {}
    // A website selection persists on reload; incoming app links still win
    // over the browser's previously saved language preference.
    const currentUrl = new URL(location.href);
    currentUrl.searchParams.set('lang', lang);
    try { history.replaceState(history.state, '', currentUrl.href); } catch (_) {}
    document.querySelectorAll('a[href*=".html"]').forEach(a => {
      const url = new URL(a.href);
      url.searchParams.set('lang', lang);
      a.href = url.href;
    });
    document.querySelectorAll('.home-link').forEach(a => a.href = './index.html?lang=' + encodeURIComponent(lang));
    const notice = document.getElementById('legal-language');
    if (notice) notice.textContent = selected.legalNotice;
  }

  let lang = 'en';
  try { lang = localStorage.getItem('mws-review-lang') || 'en'; } catch (_) {}
  lang = new URLSearchParams(location.search).get('lang') || lang;
  select?.addEventListener('change', event => setLang(event.target.value));
  setLang(lang);
})();

// Native Android selects can retain :focus-visible after a touch selection.
(() => {
  let pointer = false;
  document.addEventListener('pointerdown', () => {
    pointer = true;
    document.documentElement.dataset.inputMode = 'pointer';
  }, true);
  document.addEventListener('keydown', event => {
    if (['Tab', 'ArrowUp', 'ArrowDown', 'Enter', ' '].includes(event.key)) {
      pointer = false;
      document.documentElement.dataset.inputMode = 'keyboard';
    }
  }, true);
  document.getElementById('language')?.addEventListener('change', event => {
    if (pointer) event.currentTarget.blur();
  });
})();

