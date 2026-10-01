/* CNI Lab site — small progressive enhancements (no dependencies) */
(function () {
  'use strict';

  // --- mobile navigation -------------------------------------------------
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  // submenu: on touch/narrow screens the parent link opens the sub list first
  Array.prototype.forEach.call(document.querySelectorAll('.has-sub > a'), function (a) {
    a.addEventListener('click', function (e) {
      if (window.matchMedia('(max-width: 960px)').matches) {
        var li = a.parentNode;
        if (!li.classList.contains('is-open')) {
          e.preventDefault();
          li.classList.add('is-open');
        }
      }
    });
  });

  // --- hero keyword network: highlight a word and its links --------------
  var net = document.querySelector('.kwnet');
  if (net) {
    var links = {};   // keyword id -> {edges, node, neighbours}
    var words = {};
    Array.prototype.forEach.call(net.querySelectorAll('.kw'), function (el) {
      var id = el.getAttribute('data-kw');
      words[id] = el;
      links[id] = links[id] || { edges: [], node: null, near: [] };
    });
    Array.prototype.forEach.call(net.querySelectorAll('.kw-e line, .kw-arc path'), function (edge) {
      var a = edge.getAttribute('data-a'), b = edge.getAttribute('data-b');
      if (links[a]) { links[a].edges.push(edge); links[a].near.push(b); }
      if (links[b]) { links[b].edges.push(edge); links[b].near.push(a); }
    });
    Array.prototype.forEach.call(net.querySelectorAll('.kw-n circle'), function (dot) {
      var id = dot.getAttribute('data-n');
      if (links[id]) links[id].node = dot;
    });
    var setHot = function (id, on) {
      var l = links[id];
      if (!l) return;
      l.edges.forEach(function (e) { e.classList.toggle('is-hot', on); });
      if (l.node) l.node.classList.toggle('is-hot', on);
      l.near.forEach(function (n) { if (words[n]) words[n].classList.toggle('is-near', on); });
    };
    Object.keys(words).forEach(function (id) {
      var el = words[id];
      el.addEventListener('mouseenter', function () { setHot(id, true); });
      el.addEventListener('mouseleave', function () { setHot(id, false); });
    });
  }

  // --- publications: category switch ------------------------------------
  var catButtons = document.querySelectorAll('[data-cat-btn]');
  if (catButtons.length) {
    Array.prototype.forEach.call(catButtons, function (btn) {
      btn.addEventListener('click', function () {
        var cat = btn.getAttribute('data-cat-btn');
        Array.prototype.forEach.call(catButtons, function (b) {
          b.classList.toggle('is-on', b === btn);
        });
        Array.prototype.forEach.call(document.querySelectorAll('[data-cat-panel]'), function (p) {
          p.hidden = p.getAttribute('data-cat-panel') !== cat;
        });
        var yearNav = document.getElementById('year-nav');
        if (yearNav) yearNav.hidden = cat !== 'international';
        window.scrollTo({ top: Math.max(0, (document.getElementById('pub-top') || document.body).offsetTop - 120), behavior: 'smooth' });
      });
    });
  }

  // --- news: category filter --------------------------------------------
  var filterButtons = document.querySelectorAll('[data-filter]');
  if (filterButtons.length) {
    Array.prototype.forEach.call(filterButtons, function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter');
        Array.prototype.forEach.call(filterButtons, function (b) {
          b.classList.toggle('is-on', b === btn);
        });
        Array.prototype.forEach.call(document.querySelectorAll('[data-news-cat]'), function (card) {
          var show = f === 'all' || card.getAttribute('data-news-cat') === f;
          card.style.display = show ? '' : 'none';
        });
      });
    });
  }
})();
