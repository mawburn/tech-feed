(() => {
  'use strict';

  const elements = {
    nav: document.getElementById('date-nav'),
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
  function storyArtwork(story, small = false) {
    // Original, self-contained vector thumbnails, with a distinct design per story.
    const category = String(story.category || 'Technology');
    const title = String(story.title || 'Technology news');
    const palette = category.includes('AI') ? ['#294f67','#93d9f5'] : category.includes('Security') ? ['#49364f','#dab5f4'] : category.includes('Market') || category.includes('Business') ? ['#3c4e45','#b6e4c2'] : category.includes('Developer') || category.includes('Engineering') ? ['#3a4368','#b5c3ff'] : category.includes('Hardware') || category.includes('Quantum') ? ['#625039','#ffdea1'] : ['#31465e','#acd2e9'];
    const xml = s => String(s).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&apos;','"':'&quot;'}[c]));
    const seed = Array.from(title).reduce((n,ch)=>(n*31+ch.charCodeAt(0))>>>0,17);
    const label = xml(category.toUpperCase().slice(0,24));
    const shapes = [
      '<circle cx="304" cy="52" r="87" stroke-width="1"/><circle cx="304" cy="52" r="55" stroke-width="1.5"/><circle cx="304" cy="52" r="25" stroke-width="2"/>',
      '<path d="M210 -20 380 160 M246 -20 416 160 M282 -20 452 160 M318 -20 488 160" stroke-width="2"/><circle cx="318" cy="75" r="36" stroke-width="2"/>',
      '<path d="M220 155V96h22v59M255 155V62h22v93M290 155V36h22v119M325 155V73h22v82" stroke-width="2"/><path d="m214 98 49-42 42 9 45-48" stroke-width="3"/>',
      '<rect x="232" y="17" width="122" height="122" rx="18" stroke-width="2"/><rect x="250" y="35" width="86" height="86" rx="7" stroke-width="2"/><path d="m274 63-16 15 16 14m36-29 16 15-16 14" stroke-width="3"/>'
    ][seed % 4];
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 170"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#101926"/><stop offset="1" stop-color="'+palette[0]+'"/></linearGradient></defs><rect width="400" height="170" fill="url(#g)"/><path d="M0 124H400M0 82H400M0 40H400M80 0V170M160 0V170M240 0V170M320 0V170" fill="none" stroke="#ffffff" opacity=".055"/><g fill="none" stroke="'+palette[1]+'" opacity=".6">'+shapes+'</g><rect x="15" y="14" width="3" height="17" rx="1" fill="'+palette[1]+'"/><text x="28" y="26" font-family="Arial,sans-serif" font-size="11" font-weight="700" letter-spacing="1" fill="'+palette[1]+'">'+label+'</text><text x="17" y="151" font-family="Arial,sans-serif" font-size="11" fill="#c2d6e2" opacity=".75">MAWBURN / FEED</text></svg>';
    const img = document.createElement('img');
    img.className = small ? 'secondary-artwork' : 'story-artwork';
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    img.alt = category + ' illustration for ' + title;
    img.loading = 'lazy'; img.decoding = 'async';
    return img;
  }

  function storyCard(story, position) {
    const card = el('article','story');
    card.append(storyArtwork(story));
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
    row.append(storyArtwork(story,true),body);
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
  function renderNav() {
    elements.nav.replaceChildren();
    const buttons = [{date:'all',label:'All editions',count:state.issues.length},...state.issues.map(issue=>({date:issue.date,label:shortDate.format(dateFromISO(issue.date)),count:issueStories(issue).length}))];
    for (const item of buttons) {
      const button = el('button','day-link');
      button.type='button'; button.setAttribute('aria-pressed',String(state.day === item.date));
      append(button,el('span','day-name',item.label),el('span','day-count',item.count));
      button.addEventListener('click',()=>{state.day=item.date;render();});
      elements.nav.append(button);
    }
  }
  function render() {
    renderNav();
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
