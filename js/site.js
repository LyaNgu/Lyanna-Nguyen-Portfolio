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
    btn.className = 'navburger';
    btn.setAttribute('aria-controls', 'site-menu');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-label', 'Open menu');
    btn.innerHTML = '<span></span><span></span><span></span>';
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
