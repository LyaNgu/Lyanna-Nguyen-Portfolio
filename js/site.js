/* Shared helpers for every page: show/hide toggles, click actions and scroll reveals. */
(function () {
  'use strict';

  var actions = {};

  var Site = {
    reducedMotion: window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches,

    /* Show or hide every element marked data-show="name". */
    show: function (name, visible) {
      document.querySelectorAll('[data-show="' + name + '"]').forEach(function (el) {
        el.hidden = !visible;
      });
    },

    /* Register a handler for clicks on elements marked data-action="name". */
    on: function (name, fn) {
      actions[name] = fn;
    },

    /* Fade sections in (".rv" children) the first time they scroll into view. */
    initReveal: function () {
      var root = document.querySelector('.pp-root');
      var areas = document.querySelectorAll('[data-area]');
      if (!root || !areas.length || typeof IntersectionObserver === 'undefined') return;
      root.classList.add('js');
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('in');
            io.unobserve(e.target);
          }
        });
      }, { threshold: 0.05 });
      areas.forEach(function (el) { io.observe(el); });
    }
  };

  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('[data-action]');
    if (!el) return;
    var fn = actions[el.getAttribute('data-action')];
    if (fn) fn(e, el);
  });

  /* Phones: the top nav links collapse behind a hamburger button that opens a dropdown panel. */
  function initMenu() {
    var nav = document.querySelector('.topnav');
    var header = nav && nav.closest('header');
    if (!header) return;
    var links = nav.querySelectorAll('.navlinks');
    if (!links.length) return;

    var panel = document.createElement('div');
    panel.className = 'navpanel';
    panel.id = 'site-menu';
    panel.hidden = true;
    links.forEach(function (a) { panel.appendChild(a.cloneNode(true)); });
    header.appendChild(panel);

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pp-btn secondary navburger';
    btn.setAttribute('aria-controls', 'site-menu');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Open menu');
    btn.innerHTML = '<svg class="nb-open" viewBox="0 0 9 7" aria-hidden="true"><path d="M0 0h9v1H0zM0 3h9v1H0zM0 6h9v1H0z"/></svg>' +
      '<svg class="nb-close" viewBox="0 0 8 7" aria-hidden="true"><path d="M0 0h1v1H0zM0 6h1v1H0zM1 0h1v1H1zM1 1h1v1H1zM1 5h1v1H1zM1 6h1v1H1zM2 1h1v1H2zM2 2h1v1H2zM2 4h1v1H2zM2 5h1v1H2zM3 2h1v1H3zM3 3h1v1H3zM3 4h1v1H3zM4 2h1v1H4zM4 3h1v1H4zM4 4h1v1H4zM5 1h1v1H5zM5 2h1v1H5zM5 4h1v1H5zM5 5h1v1H5zM6 0h1v1H6zM6 1h1v1H6zM6 5h1v1H6zM6 6h1v1H6zM7 0h1v1H7zM7 6h1v1H7z"/></svg>';
    nav.appendChild(btn);

    function set(open) {
      panel.hidden = !open;
      btn.setAttribute('aria-expanded', String(open));
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      header.classList.toggle('menu-open', open);
    }
    btn.addEventListener('click', function () { set(panel.hidden); });
    panel.addEventListener('click', function (e) { if (e.target.closest('a')) set(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hidden) { set(false); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (!panel.hidden && !header.contains(e.target)) set(false);
    });
    window.addEventListener('resize', function () { if (window.innerWidth > 760) set(false); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initMenu);
  else initMenu();

  window.Site = Site;
})();
