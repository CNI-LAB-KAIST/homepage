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

  // --- news: build the year buttons from the cards -----------------------
  var yearBox = document.querySelector('[data-year-filter]');
  if (yearBox) {
    var years = [];
    Array.prototype.forEach.call(document.querySelectorAll('[data-news-year]'), function (card) {
      var y = card.getAttribute('data-news-year');
      if (y && years.indexOf(y) === -1) years.push(y);
    });
    years.sort(function (a, b) { return b - a; });
    var html = '<button type="button" class="is-on" data-filter="all">All</button>';
    years.forEach(function (y) {
      html += '<button type="button" data-filter="' + y + '">' + y + '</button>';
    });
    yearBox.innerHTML = html;
  }

  // --- news: year filter --------------------------------------------
  var filterButtons = document.querySelectorAll('[data-filter]');
  if (filterButtons.length) {
    Array.prototype.forEach.call(filterButtons, function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter');
        Array.prototype.forEach.call(filterButtons, function (b) {
          b.classList.toggle('is-on', b === btn);
        });
        Array.prototype.forEach.call(document.querySelectorAll('[data-news-year]'), function (card) {
          var show = f === 'all' || card.getAttribute('data-news-year') === f;
          card.style.display = show ? '' : 'none';
        });
      });
    });
  }
})();

/* lab life slideshow */
document.querySelectorAll('[data-slideshow]').forEach(function(box){
  var slides=[].slice.call(box.querySelectorAll('.slide')),
      dots=[].slice.call(box.querySelectorAll('.sl-dots button')),i=0,timer=null;
  if(slides.length<2) return;
  function show(n){i=(n+slides.length)%slides.length;
    slides.forEach(function(s,k){s.classList.toggle('is-on',k===i);});
    dots.forEach(function(d,k){d.classList.toggle('is-on',k===i);});}
  function play(){stop();timer=setInterval(function(){show(i+1);},5200);}
  function stop(){if(timer){clearInterval(timer);timer=null;}}
  box.querySelector('.sl-next').addEventListener('click',function(){show(i+1);play();});
  box.querySelector('.sl-prev').addEventListener('click',function(){show(i-1);play();});
  dots.forEach(function(d,k){d.addEventListener('click',function(){show(k);play();});});
  box.addEventListener('mouseenter',stop); box.addEventListener('mouseleave',play);
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches) play();
});

/* 이미지 우클릭 저장 / 드래그 저장 막기 (로고 등 링크 안의 이미지는 제외) */
document.addEventListener('contextmenu', function (e) {
  var img = e.target && e.target.closest ? e.target.closest('img') : null;
  if (img && !img.closest('a')) e.preventDefault();
});
document.addEventListener('dragstart', function (e) {
  var img = e.target && e.target.closest ? e.target.closest('img') : null;
  if (img) e.preventDefault();
});
