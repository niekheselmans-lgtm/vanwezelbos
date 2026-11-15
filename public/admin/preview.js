/* Preview in het beheerscherm: toont het bericht zoals op de echte site,
   met een knop om te wisselen tussen desktop, tablet en telefoon. */
(function () {
  var MONTHS = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
    'augustus', 'september', 'oktober', 'november', 'december'];
  var CATS = { werkzaamheden: 'Werkzaamheden', algemeen: 'Algemeen' };
  var DEVICES = [
    { id: 'desktop', label: 'Desktop', w: 1280, h: 900 },
    { id: 'tablet', label: 'Tablet', w: 820, h: 1000 },
    { id: 'phone', label: 'Telefoon', w: 390, h: 800 }
  ];

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  /* Zelfde regels als scripts/build.py, zodat preview en echte site gelijk zijn. */
  function makeMd(asset) {
    function inline(text) {
      var t = esc(text);
      t = t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, function (m, alt, src) {
        return '<img src="' + asset(src) + '" alt="' + alt + '">';
      });
      t = t.replace(/\[([^\]]+)\]\(((?:https?:\/\/|mailto:|\/|#)[^)\s]*)\)/g, '<a href="$2">$1</a>');
      t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
      t = t.replace(/\*\*(.+?)\*\*|__(.+?)__/g, function (m, a, b) { return '<strong>' + (a || b) + '</strong>'; });
      t = t.replace(/(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])/g, '<em>$1</em>');
      t = t.replace(/(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])/g, '<em>$1</em>');
      return t;
    }
    return function (md) {
      var out = [];
      String(md || '').replace(/\r\n/g, '\n').trim().split(/\n\s*\n/).forEach(function (block) {
        block = block.replace(/^\n+|\n+$/g, '');
        if (!block.trim()) return;
        var lines = block.split('\n'), m;
        if ((m = lines[0].match(/^(#{1,6})\s+(.*)$/)) && lines.length === 1) {
          var lvl = m[1].length <= 2 ? 2 : 3;
          out.push('<h' + lvl + '>' + inline(m[2].trim()) + '</h' + lvl + '>');
        } else if (/^[-*_]{3,}$/.test(block.trim())) {
          out.push('<hr>');
        } else if ((m = block.trim().match(/^!\[([^\]]*)\]\(([^)\s]+)\)$/))) {
          out.push('<figure><img src="' + asset(m[2]) + '" alt="' + esc(m[1]) + '">' +
            (m[1] ? '<figcaption>' + esc(m[1]) + '</figcaption>' : '') + '</figure>');
        } else if (lines.every(function (l) { return /^\s*[-*+]\s+/.test(l); })) {
          out.push('<ul>' + lines.map(function (l) { return '<li>' + inline(l.replace(/^\s*[-*+]\s+/, '')) + '</li>'; }).join('') + '</ul>');
        } else if (lines.every(function (l) { return /^\s*\d+[.)]\s+/.test(l); })) {
          out.push('<ol>' + lines.map(function (l) { return '<li>' + inline(l.replace(/^\s*\d+[.)]\s+/, '')) + '</li>'; }).join('') + '</ol>');
        } else if (lines.every(function (l) { return l.charAt(0) === '>'; })) {
          out.push('<blockquote><p>' + inline(lines.map(function (l) { return l.replace(/^>\s?/, '').trim(); }).join(' ')) + '</p></blockquote>');
        } else {
          out.push('<p>' + inline(lines.map(function (l) { return l.trim(); }).join(' ')) + '</p>');
        }
      });
      return out.join('\n');
    };
  }

  function dateLabel(v) {
    var s = '';
    if (typeof v === 'string') s = v.slice(0, 10);
    else if (v && v.toISOString) s = v.toISOString().slice(0, 10);
    var m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/) || s.match(/^(\d{2})-(\d{2})-(\d{4})$/);
    if (!m) return '';
    var y, mo, d;
    if (s.charAt(4) === '-') { y = +m[1]; mo = +m[2]; d = +m[3]; } else { d = +m[1]; mo = +m[2]; y = +m[3]; }
    return d + ' ' + MONTHS[mo - 1] + ' ' + y;
  }

  function pageHtml(props) {
    var entry = props.entry;
    function get(k) { return entry.getIn(['data', k]); }
    function asset(p) {
      if (!p) return '';
      try { return String(props.getAsset(p)) || p; } catch (e) { return p; }
    }
    var title = get('title') || 'Titel van je bericht';
    var cat = CATS[get('category')] || 'Werkzaamheden';
    var date = dateLabel(get('date'));
    var img = get('image');
    var md = makeMd(asset);
    var body = md(get('body')) || '<div style="color:#888">Hier verschijnt je tekst…</div>';
    var hero = img
      ? '<div class="wrap post-hero"><img src="' + asset(img) + '" alt=""></div>'
      : '<div class="wrap post-hero"><div style="height:260px;border-radius:18px;background:#dfe6d3;display:grid;place-items:center;color:#5d7a4a;font:700 1.05rem Carlito,Calibri,sans-serif">Nog geen afbeelding gekozen</div></div>';
    return '<!doctype html><html lang="nl"><head><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width, initial-scale=1">' +
      '<base href="' + location.origin + '/">' +
      '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' +
      '<link href="https://fonts.googleapis.com/css2?family=Carlito:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">' +
      '<link rel="stylesheet" href="/css/style.css"><style>.site-header{position:static}</style></head><body>' +
      '<header class="site-header"><div class="wrap bar"><span class="brand"><svg viewBox="0 0 32 32" width="26" height="26"><path d="M16 2 6 15h5l-4 7h6v6h6v-6h6l-4-7h5z" fill="currentColor"/></svg><span>Van Wezelbos</span></span></div></header>' +
      '<main><article class="post"><header class="post-head" style="padding-top:40px"><div class="wrap narrow">' +
      '<span class="back">← Alle berichten</span><br><span class="tag">' + esc(cat) + (date ? ' · ' + esc(date) : '') + '</span>' +
      '<h1>' + esc(title) + '</h1></div></header>' + hero +
      '<div class="wrap narrow prose" style="padding-bottom:60px">' + body + '</div></article></main></body></html>';
  }

  var Preview = createClass({
    getInitialState: function () { return { device: 'desktop', avail: 700 }; },
    componentDidMount: function () {
      var self = this;
      this.measure = function () {
        if (self.wrap && self.wrap.clientWidth && Math.abs(self.wrap.clientWidth - self.state.avail) > 1) {
          self.setState({ avail: self.wrap.clientWidth });
        }
      };
      this.measure();
      this.timer = setInterval(this.measure, 300);
    },
    componentWillUnmount: function () { clearInterval(this.timer); },
    render: function () {
      var self = this;
      var dev = DEVICES.filter(function (d) { return d.id === self.state.device; })[0];
      var scale = Math.min(1, (this.state.avail - 8) / dev.w);
      var isPhone = dev.id === 'phone';
      var bar = h('div', { style: { display: 'flex', gap: '8px', justifyContent: 'center', padding: '12px 8px', background: '#f1efe8', fontFamily: 'Carlito, Calibri, sans-serif', position: 'sticky', top: 0, zIndex: 5 } },
        DEVICES.map(function (d) {
          var on = d.id === dev.id;
          return h('button', {
            key: d.id, type: 'button',
            onClick: function () { self.setState({ device: d.id }); },
            style: { cursor: 'pointer', border: '1px solid ' + (on ? '#1c3326' : '#d6d1c2'), background: on ? '#1c3326' : '#fff', color: on ? '#fff' : '#1c3326', font: '700 14px Carlito, Calibri, sans-serif', padding: '8px 16px', borderRadius: '99px' }
          }, d.label + ' · ' + d.w + 'px');
        }));
      return h('div', { style: { background: '#e9e6dc', minHeight: '100vh' } }, bar,
        h('div', { ref: function (el) { self.wrap = el; }, style: { padding: '16px 4px 40px' } },
          h('div', { style: { width: Math.round(dev.w * scale), height: Math.round(dev.h * scale), margin: '0 auto', overflow: 'hidden', borderRadius: isPhone ? 28 * scale : 10, boxShadow: '0 10px 40px -10px rgba(0,0,0,.35)', background: '#fff', border: isPhone ? '6px solid #14241b' : '1px solid #cfc9b6', boxSizing: 'content-box' } },
            h('iframe', { title: 'Voorbeeld', srcDoc: pageHtml(this.props), style: { width: dev.w, height: dev.h, border: 0, transform: 'scale(' + scale + ')', transformOrigin: 'top left', display: 'block', background: '#fff' } }))),
        h('p', { style: { textAlign: 'center', font: '15px Carlito, Calibri, sans-serif', color: '#5f685f', margin: '0 0 24px' } }, 'Zo ziet je bericht eruit zodra je op Publiceren klikt.'));
    }
  });

  CMS.registerPreviewTemplate('posts', Preview);
  window.__previewHelpers = { makeMd: makeMd, dateLabel: dateLabel };
})();
