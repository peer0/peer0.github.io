/* Progressive enhancement: content and navigation are usable without scripts. */
(() => {
  'use strict';
  const menuButton = document.querySelector('[data-menu-toggle]');
  const navigation = document.querySelector('#site-navigation');
  if (menuButton && navigation) {
    menuButton.hidden = false;
    navigation.classList.add('enhanced');
    const closeMenu = () => {
      menuButton.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
    };
    menuButton.addEventListener('click', () => {
      const open = menuButton.getAttribute('aria-expanded') !== 'true';
      menuButton.setAttribute('aria-expanded', String(open));
      navigation.classList.toggle('is-open', open);
    });
    navigation.addEventListener('click', event => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        menuButton.focus();
      }
    });
  }
  const status = document.querySelector('#action-status');
  let statusTimer;
  const announce = message => {
    if (!status) return;
    window.clearTimeout(statusTimer);
    status.textContent = message;
    status.classList.add('has-message');
    statusTimer = window.setTimeout(() => {
      status.classList.remove('has-message');
      status.textContent = '';
    }, 6000);
  };
  document.querySelectorAll('[data-copy-target]').forEach(button => {
    const target = document.getElementById(button.dataset.copyTarget);
    if (!target) return;
    button.hidden = false;
    button.addEventListener('click', async () => {
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(target.textContent.trim());
        announce('Reference copied.');
      } catch (_) {
        // Local previews may not allow clipboard writes. Offer a truthful fallback.
        target.focus();
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(target);
        if (selection) {
          selection.removeAllRanges();
          selection.addRange(range);
        }
        announce('Select the reference and press Ctrl+C or ⌘C to copy.');
      }
    });
  });
  const controls = document.querySelector('[data-publication-controls]');
  if (!controls) return;
  controls.hidden = false;
  const papers = Array.from(document.querySelectorAll('[data-paper]'));
  const sections = Array.from(document.querySelectorAll('[data-year-group]'));
  const search = document.querySelector('#publication-search');
  const year = document.querySelector('#publication-year');
  const type = document.querySelector('#publication-type');
  const count = document.querySelector('#publication-count');
  const empty = document.querySelector('#no-publications');
  const reset = document.querySelector('#reset-filters');
  const topics = Array.from(document.querySelectorAll('[data-topic-filter]'));
  const params = new URLSearchParams(window.location.search);
  // A topic link may name several topics, e.g. ?topic=formal,language from the home page.
  const known = new Set(topics.map(button => button.dataset.topicFilter));
  const requested = (params.get('topic') || '').split(',').filter(value => value && value !== 'all' && known.has(value));
  let topic = requested.length ? requested.join(',') : 'all';
  const topicSet = () => new Set(topic.split(','));
  search.value = params.get('q') || '';
  if (Array.from(year.options).some(option => option.value === params.get('year'))) year.value = params.get('year');
  if (Array.from(type.options).some(option => option.value === params.get('type'))) type.value = params.get('type');
  const normalize = value => value.toLocaleLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  const update = () => {
    const words = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    papers.forEach(paper => {
      const text = normalize(paper.dataset.search || paper.textContent);
      const match = (topic === 'all' || topicSet().has(paper.dataset.topic))
        && (year.value === 'all' || paper.dataset.year === year.value)
        && (type.value === 'all' || paper.dataset.type === type.value)
        && words.every(word => text.includes(word));
      paper.hidden = !match;
      if (match) visible += 1;
    });
    sections.forEach(section => { section.hidden = !section.querySelector('[data-paper]:not([hidden])'); });
    topics.forEach(button => button.setAttribute('aria-pressed', String(topicSet().has(button.dataset.topicFilter))));
    count.textContent = `${visible} of ${papers.length} publications`;
    empty.hidden = visible !== 0;
    reset.hidden = topic === 'all' && year.value === 'all' && type.value === 'all' && !search.value;
    const next = new URLSearchParams();
    if (topic !== 'all') next.set('topic', topic);
    if (year.value !== 'all') next.set('year', year.value);
    if (type.value !== 'all') next.set('type', type.value);
    if (search.value.trim()) next.set('q', search.value.trim());
    try {
      const query = next.toString();
      history.replaceState(null, '', `${location.pathname}${query ? `?${query}` : ''}${location.hash}`);
    } catch (_) {
      /* Search still works in local-file and embedded previews. */
    }
  };
  search.addEventListener('input', update);
  document.addEventListener('keydown', event => {
    const editing = event.target instanceof Element && event.target.closest('input, textarea, select, [contenteditable]:not([contenteditable="false"])');
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !event.isComposing && !event.defaultPrevented && !editing) {
      event.preventDefault();
      search.focus();
    }
  });
  year.addEventListener('change', update);
  type.addEventListener('change', update);
  topics.forEach(button => button.addEventListener('click', () => {
    topic = button.dataset.topicFilter;
    update();
  }));
  reset.addEventListener('click', () => {
    search.value = '';
    year.value = 'all';
    type.value = 'all';
    topic = 'all';
    update();
    search.focus();
  });
  update();
})();
