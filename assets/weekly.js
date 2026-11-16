(() => {
  'use strict';
  const nav = document.getElementById('week-nav');
  const content = document.getElementById('weekly-content');
  const count = document.getElementById('weekly-count');
  const archiveCount = document.getElementById('weekly-archive-count');
  const longDate = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', month: 'long', day: 'numeric', year: 'numeric' });
  const shortDate = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric' });
  const state = { weeks: [], selected: null };

  function el(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value != null) node.textContent = String(value);
    return node;
  }
  function append(parent, ...children) { parent.append(...children); return parent; }
  function date(iso) { return new Date(iso + 'T12:00:00Z'); }
  function formatWeek(week) {
    return shortDate.format(date(week.weekStart)) + ' – ' + longDate.format(date(week.weekEnding));
  }
  function safeUrl(input) {
    try {
      const u = new URL(String(input));
      return ['https:', 'http:'].includes(u.protocol) ? u.href : null;
    } catch { return null; }
  }
  function sourceRow(links) {
    const row = el('div', 'weekly-source-links');
    for (const link of Array.isArray(links) ? links : []) {
      const url = safeUrl(link?.url);
      if (!url) continue;
      const anchor = el('a', 'source-link', (link.label || new URL(url).hostname) + ' ↗');
      anchor.href = url;
      anchor.target = '_blank';
      anchor.rel = 'noopener noreferrer';
      row.append(anchor);
    }
    return row.childElementCount ? row : null;
  }
  function storyImage(story) {
    const image = story?.image;
    const url = safeUrl(image?.url);
    if (!url) return null;
    const figure = el('figure', 'weekly-figure');
    const img = document.createElement('img');
    img.src = url;
    img.loading = 'lazy';
    img.decoding = 'async';
    img.referrerPolicy = 'no-referrer';
    img.alt = image.alt || 'Publisher image accompanying ' + story.title;
    img.addEventListener('error', () => figure.remove());
    figure.append(img);
    if (image.credit) figure.append(el('figcaption', 'image-credit', 'Image: ' + image.credit));
    return figure;
  }
  function themeCard(theme, i) {
    const card = el('article', 'weekly-theme');
    const image = storyImage(theme);
    if (image) card.append(image);
    const top = el('div', 'weekly-theme-meta');
    append(top, el('span', 'story-rank', String(i + 1).padStart(2, '0')), el('span', 'story-category', theme.category || 'Technology'));
    append(card, top, el('h3', 'weekly-theme-title', theme.title || 'Untitled development'));
    if (theme.summary) card.append(el('p', 'weekly-theme-summary', theme.summary));
    if (theme.impact) {
      const p = el('p', 'story-insight');
      append(p, el('strong', '', 'Why it matters: '), document.createTextNode(theme.impact));
      card.append(p);
    }
    if (theme.caveat) {
      const p = el('p', 'story-insight story-limit');
      append(p, el('strong', '', 'Caveat: '), document.createTextNode(theme.caveat));
      card.append(p);
    }
    const sources = sourceRow(theme.links);
    if (sources) card.append(sources);
    return card;
  }
  function toolCard(tool) {
    const card = el('article', 'weekly-tool');
    append(card, el('h3', '', tool.title || 'Tool'), el('p', '', tool.summary || ''));
    const links = sourceRow(tool.links);
    if (links) card.append(links);
    return card;
  }
  function section(title, className, children) {
    if (!children.length) return null;
    const block = el('section', className);
    append(block, el('h2', 'section-label', title), ...children);
    return block;
  }
  function renderNav() {
    nav.replaceChildren();
    for (const week of state.weeks) {
      const button = el('button', 'day-link weekly-nav-item');
      button.type = 'button';
      button.setAttribute('aria-pressed', String(state.selected === week.weekEnding));
      append(button, el('span', 'day-name', shortDate.format(date(week.weekEnding))), el('span', 'day-count', week.themes?.length ?? 0));
      button.addEventListener('click', () => {
        state.selected = week.weekEnding;
        render();
      });
      nav.append(button);
    }
  }
  function render() {
    renderNav();
    const week = state.weeks.find(w => w.weekEnding === state.selected);
    if (!week) {
      const box = el('div', 'empty-state');
      append(box, el('h3', '', 'No weekly summary yet'), el('p', '', 'A new summary is scheduled for Sundays.'));
      content.replaceChildren(box);
      return;
    }
    const root = el('article', 'weekly-edition');
    const head = el('header', 'edition-header');
    const label = week.partial ? 'PARTIAL WEEK · ' + week.coverageDays + ' DAILY EDITIONS' : 'WEEKLY REVIEW';
    append(head, el('p', 'edition-kicker', label), el('h2', 'edition-date', formatWeek(week)), el('h3', 'weekly-headline', week.title || 'Weekly news summary'));
    if (week.overview) head.append(el('p', 'weekly-overview', week.overview));
    root.append(head);

    const themes = section('The developments that mattered', 'weekly-theme-section',
      (week.themes || []).map(themeCard));
    if (themes) root.append(themes);

    const tools = section('Tools worth investigating', 'weekly-tools-section',
      (week.toolsToWatch || []).map(toolCard));
    if (tools) root.append(tools);

    if (week.marketPulse) {
      const pulse = section('Industry and job market', 'weekly-market-section', [el('p', 'pulse', week.marketPulse)]);
      root.append(pulse);
    }
    if (week.nextWeekWatch) {
      const watch = section('What to watch next week', 'weekly-next-section', [el('p', 'pulse', week.nextWeekWatch)]);
      root.append(watch);
    }
    if ((week.sourceDays || []).length) {
      const detail = el('p', 'weekly-coverage-note');
      detail.textContent = 'Daily briefings included: ' + week.sourceDays.join(', ') + '. ';
      const daily = el('a', '', 'Browse daily feed ↗');
      daily.href = './';
      detail.append(daily);
      root.append(detail);
    }
    content.replaceChildren(root);
  }
  document.getElementById('copyright-year').textContent = new Date().getFullYear();
  fetch('./data/weekly.json', { cache: 'no-store' })
    .then(response => {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    })
    .then(data => {
      if (data?.schemaVersion !== 1 || !Array.isArray(data.weeks)) throw new Error('Unexpected weekly summary schema');
      const unique = new Map();
      for (const week of data.weeks) {
        if (typeof week?.weekEnding !== 'string' || typeof week?.weekStart !== 'string') continue;
        if (!unique.has(week.weekEnding)) unique.set(week.weekEnding, week);
      }
      state.weeks = [...unique.values()].sort((a,b) => b.weekEnding.localeCompare(a.weekEnding));
      state.selected = state.weeks[0]?.weekEnding || null;
      count.textContent = state.weeks.length + (state.weeks.length === 1 ? ' edition' : ' editions');
      archiveCount.textContent = 'Sunday recaps · newest first';
      render();
    })
    .catch(error => {
      console.error('Unable to load weekly recaps', error);
      const box = el('div', 'empty-state');
      append(box, el('h3', '', 'Summary unavailable'), el('p', '', 'The weekly recap data could not be loaded. Please try again later.'));
      content.replaceChildren(box);
      count.textContent = 'Unavailable';
    });
})();
