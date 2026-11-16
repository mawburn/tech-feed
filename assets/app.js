(() => {
  'use strict';

  const elements = {
    nav: document.getElementById('date-nav'),
    topicNav: document.getElementById('topic-nav'),
    topicSummary: document.getElementById('topic-summary'),
    content: document.getElementById('feed-content'),
    count: document.getElementById('results-count'),
    archive: document.getElementById('archive-count'),
    updated: document.getElementById('latest-update'),
    category: document.getElementById('category'),
    search: document.getElementById('search'),
  };
  const state = { issues: [], day: 'all', category: 'all', query: '' };
  const longDate = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const shortDate = new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric' });

  function el(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value != null) node.textContent = String(value);
    return node;
  }
  function append(parent, ...children) { parent.append(...children); return parent; }
  function dateFromISO(day) { return new Date(`${day}T12:00:00Z`); }
  function pacificToday() {
    const parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date());
    const obj = Object.fromEntries(parts.map(({type,value}) => [type,value]));
    return `${obj.year}-${obj.month}-${obj.day}`;
  }
  function sevenDayStart(today) {
    const [year, month, day] = today.split('-').map(Number);
    return new Date(Date.UTC(year, month-1, day-6)).toISOString().slice(0,10);
  }
  function safeLink(data, className='source-link') {
    if (!data || typeof data.url !== 'string') return null;
    let url;
    try { url = new URL(data.url); } catch { return null; }
    if (!['http:', 'https:'].includes(url.protocol)) return null;
    const link = el('a', className, (data.label || url.hostname.replace(/^www\./,'')) + ' ↗');
    link.href = url.toString();
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    return link;
  }
  function sourcesRow(sources, compact = false) {
    const items = Array.isArray(sources) ? sources.map(item => safeLink(item, compact ? '' : 'source-link')).filter(Boolean) : [];
    if (!items.length) return null;
    const row = el('div', compact ? 'secondary-links' : 'source-row');
    if (!compact) row.append(el('span','source-label','Sources'));
    row.append(...items);
    return row;
  }
  function textMatch(item) {
    const cat = item.category || 'Other';
    if (state.category !== 'all' && cat !== state.category) return false;
    if (!state.query) return true;
    return [item.title, item.summary, item.whyItMatters, item.limitations, cat].filter(Boolean).join(' ').toLowerCase().includes(state.query);
  }
  function issueStories(issue) {
    return [...(issue.topStories || []), ...(issue.alsoWorthKnowing || []), ...(issue.newTools || [])];
  }
  function storyImage(story, small = false) {
    const image = story.image;
    if (!image || typeof image.url !== 'string') return null;
    let url;
    try { url = new URL(image.url); } catch { return null; }
    if (url.protocol !== 'https:' && url.protocol !== 'http:') return null;
    const figure = el('figure', small ? 'secondary-image' : 'story-image');
    const img = document.createElement('img');
    img.className = small ? 'secondary-artwork' : 'story-artwork';
    img.src = url.href;
    img.loading = 'lazy';
    img.decoding = 'async';
    img.alt = image.alt || (story.title ? 'Image accompanying ' + story.title : 'Article image');
    img.referrerPolicy = 'no-referrer';
    img.addEventListener('error', () => figure.remove());
    figure.append(img);
    if (image.credit) figure.append(el('figcaption','image-credit','Image: ' + image.credit));
    return figure;
  }

  function storyCard(story, position) {
    const card = el('article','story');
    const artwork = storyImage(story);
    if (artwork) card.append(artwork);
    const header = el('div','story-header');
    append(header, el('span','story-rank',String(story.rank || position).padStart(2,'0')), el('span','story-category',story.category || 'Technology'));
    if (story.isUpdate) header.append(el('span','story-updated','UPDATED'));
    append(card,header,el('h4','story-title',story.title || 'Untitled story'));
    if (story.summary) card.append(el('p','story-summary',story.summary));
    for (const [title,key,css] of [['Why it matters','whyItMatters','story-insight'],['Caveat','limitations','story-insight story-limit']]) {
      if (story[key]) {
        const p = el('p',css);
        append(p,el('strong','',`${title}: `),document.createTextNode(story[key]));
        card.append(p);
      }
    }
    const row = sourcesRow(story.sources);
    if (row) card.append(row);
    return card;
  }
  function secondaryStory(story) {
    const row = el('article','secondary-story');
    const body = el('div','secondary-copy');
    const header = el('div','secondary-header');
    append(header,el('h4','secondary-title',story.title || 'Untitled'),el('span','secondary-category',story.category || 'Technology'));
    body.append(header);
    if (story.summary) body.append(el('p','',story.summary));
    const links = sourcesRow(story.sources,true);
    if (links) body.append(links);
    const artwork = storyImage(story,true);
    if (artwork) row.append(artwork);
    else row.classList.add('no-image');
    row.append(body);
    return row;
  }
  function section(title, items, renderItem) {
    if (!items.length) return null;
    const wrapper = el('section');
    append(wrapper,el('h3','section-label',title),...items.map(renderItem));
    return wrapper;
  }
  function issueCard(issue) {
    const top = (issue.topStories || []).filter(textMatch);
    const also = (issue.alsoWorthKnowing || []).filter(textMatch);
    const tools = (issue.newTools || []).filter(textMatch);
    if (!top.length && !also.length && !tools.length && (state.category!=='all' || state.query)) return null;
    const parent = el('section','edition');
    parent.id = `edition-${issue.date}`;
    const header = el('header','edition-header');
    append(header,el('p','edition-kicker', issue.label || 'Daily edition'),el('h2','edition-date',longDate.format(dateFromISO(issue.date))));
    if (issue.overview && state.category === 'all' && !state.query) header.append(el('p','edition-overview',issue.overview));
    parent.append(header);
    const tops = section('Top stories',top,(item,i)=>storyCard(item,i+1));
    const worth = section('Also worth knowing',also,secondaryStory);
    const newTools = section('Tools, models & repositories',tools,secondaryStory);
    for (const block of [tops,worth,newTools]) if (block) parent.append(block);
    if (issue.marketPulse && state.category === 'all' && !state.query) {
      const pulse = el('section');
      append(pulse,el('h3','section-label','Job market & business pulse'),el('div','pulse',issue.marketPulse));
      parent.append(pulse);
    }
    return parent;
  }
  function renderTopics() {
    const issues = state.day === 'all' ? state.issues : state.issues.filter(issue => issue.date === state.day);
    const counts = new Map();
    let total = 0;
    for (const issue of issues) {
      for (const story of issueStories(issue)) {
        const category = story.category || 'Other';
        counts.set(category, (counts.get(category) || 0) + 1);
        total++;
      }
    }
    elements.topicNav.replaceChildren();
    elements.topicSummary.textContent = `${counts.size} ${counts.size === 1 ? 'topic' : 'topics'} · ${total} stories`;
    const options = [{name: 'All topics', value: 'all', count: total},
      ...Array.from(counts, ([name, count]) => ({name, value: name, count}))
        .sort((a,b) => b.count - a.count || a.name.localeCompare(b.name))];
    for (const option of options) {
      const button = el('button', 'topic-link');
      button.type = 'button';
      button.setAttribute('aria-pressed', String(state.category === option.value));
      append(button, el('span','topic-name',option.name), el('span','topic-count',option.count));
      button.addEventListener('click', () => {
        state.category = option.value;
        elements.category.value = state.category;
        render();
      });
      elements.topicNav.append(button);
    }
  }

  function renderNav() {
    elements.nav.replaceChildren();
    const buttons = [{date:'all',label:'All editions',count:state.issues.length},...state.issues.map(issue=>({date:issue.date,label:shortDate.format(dateFromISO(issue.date)),count:issueStories(issue).length}))];
    for (const item of buttons) {
      const button = el('button','day-link');
      button.type='button'; button.setAttribute('aria-pressed',String(state.day === item.date));
      append(button,el('span','day-name',item.label),el('span','day-count',item.count));
      button.addEventListener('click',()=>{state.day=item.date;state.category='all';elements.category.value='all';render();});
      elements.nav.append(button);
    }
  }
  function render() {
    renderNav();
    renderTopics();
    const issues = state.day==='all' ? state.issues : state.issues.filter(i=>i.date===state.day);
    const matches = issues.flatMap(issue=>issueStories(issue).filter(textMatch));
    elements.count.textContent = `${matches.length} ${matches.length===1?'story':'stories'}`;
    const sections = issues.map(issueCard).filter(Boolean);
    if (sections.length) elements.content.replaceChildren(...sections);
    else {
      const empty=el('div','empty-state');
      append(empty,el('h3','',state.issues.length?'No matching stories':'No editions published yet'),el('p','',state.issues.length?'Try a different search, topic, or date.':'The next daily briefing will appear here after it is published.'));
      elements.content.replaceChildren(empty);
    }
  }
  function init(data) {
    if (!data || data.schemaVersion !== 1 || !Array.isArray(data.issues)) throw new Error('Invalid feed format');
    const today=pacificToday(), start=sevenDayStart(today);
    const unique = new Map();
    for (const issue of data.issues) {
      if (!issue || !/^\d{4}-\d{2}-\d{2}$/.test(issue.date) || issue.date < start || issue.date > today) continue;
      if (!unique.has(issue.date)) unique.set(issue.date,issue);
    }
    state.issues = Array.from(unique.values()).sort((a,b)=>b.date.localeCompare(a.date));
    state.day = state.issues[0]?.date || 'all';
    elements.archive.textContent = `${state.issues.length} of 7 possible editions`;
    elements.updated.textContent = state.issues.length ? `Latest edition · ${shortDate.format(dateFromISO(state.issues[0].date))}` : 'Awaiting first edition';
    const categories = new Set(state.issues.flatMap(issue=>issueStories(issue).map(story=>story.category).filter(Boolean)));
    for (const cat of Array.from(categories).sort()) {const option=el('option','',cat);option.value=cat;elements.category.append(option);}
    render();
  }
  elements.category.addEventListener('change',e=>{state.category=e.target.value;render();});
  elements.search.addEventListener('input',e=>{state.query=e.target.value.trim().toLowerCase();render();});
  document.getElementById('copyright-year').textContent = new Date().getFullYear();
  fetch('./data/briefings.json',{cache:'no-store'})
    .then(response=>{if(!response.ok)throw new Error(`HTTP ${response.status}`);return response.json();})
    .then(init)
    .catch(error=>{
      console.error('Unable to load feed:',error);
      const empty=el('div','empty-state');
      append(empty,el('h3','','Feed unavailable'),el('p','','The briefing data could not be loaded. Please refresh later.'));
      elements.content.replaceChildren(empty);
      elements.updated.textContent = 'Unable to load latest edition';
    });
})();
