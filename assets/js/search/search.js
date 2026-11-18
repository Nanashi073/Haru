// 覆盖主题的 search.js。
// 主题原本用 FlexSearch，它按空格/标点分词，对中文基本搜不到；
// 博客只有几十篇文章，直接在浏览器里做子串匹配，又快又准。
// 索引来自 /searchindex.json（hugo.toml 里的 SearchIndex 输出 + 主题的 home.searchindex.json 模板）。
import * as params from '@params';

(function () {
  const form = document.querySelector('.search-form');
  if (!form) return;

  const input = document.querySelector('.search-text');
  const results = document.querySelector('.search-results');
  const template = document.querySelector('template').content;
  const loading = document.querySelector('.search-loading');
  const limit = params.searchLimit || 20;
  let pages = [];

  const escapeHTML = (s) =>
    s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  // 取关键词第一次出现位置前后的一段文字，并高亮所有关键词
  function snippet(text, terms) {
    const lower = text.toLowerCase();
    let pos = -1;
    for (const t of terms) {
      const i = lower.indexOf(t);
      if (i !== -1 && (pos === -1 || i < pos)) pos = i;
    }
    if (pos === -1) return '';
    const start = Math.max(0, pos - 40);
    const end = Math.min(text.length, pos + 80);
    let s = escapeHTML(text.slice(start, end));
    const re = new RegExp('(' + terms.map((t) => escapeRegExp(escapeHTML(t))).join('|') + ')', 'gi');
    s = s.replace(re, '<mark>$1</mark>');
    return (start > 0 ? '…' : '') + s + (end < text.length ? '…' : '');
  }

  function search(q) {
    // 空格分隔多个关键词，需全部命中
    const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    results.textContent = '';
    if (!terms.length) return;

    const hits = [];
    for (const p of pages) {
      const title = (p.title || '').toLowerCase();
      const hay = title + '\n' + (p.tags || '').toLowerCase() + '\n' + p._content;
      if (!terms.every((t) => hay.includes(t))) continue;
      // 标题命中的排前面，其余保持原顺序（按日期从新到旧）
      const score = terms.filter((t) => title.includes(t)).length;
      hits.push({ p, score });
    }
    hits.sort((a, b) => b.score - a.score);

    const fragment = document.createDocumentFragment();
    if (!hits.length) {
      const empty = document.createElement('p');
      empty.className = 'dim';
      empty.textContent = '没有找到相关文章';
      fragment.appendChild(empty);
    }
    for (const { p } of hits.slice(0, limit)) {
      const node = template.cloneNode(true);
      const a = node.querySelector('a');
      a.textContent = p.title;
      a.href = p.permalink;
      node.querySelector('time').textContent = p.date;
      node.querySelector('.content').innerHTML = snippet(p.content || '', terms) || escapeHTML(p.summary || '');
      fragment.appendChild(node);
    }
    results.appendChild(fragment);
  }

  loading.classList.remove('hidden');
  fetch(params.basePath + 'searchindex.json')
    .then((r) => r.json())
    .then((data) => {
      pages = data.map((p) => ({ ...p, _content: (p.content || '').toLowerCase() }));
      loading.classList.add('hidden');
      const q = new URLSearchParams(window.location.search).get('q') || '';
      input.value = q;
      input.focus();
      search(q);
    });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    search(input.value);
  });
  input.addEventListener('input', () => search(input.value));
})();
