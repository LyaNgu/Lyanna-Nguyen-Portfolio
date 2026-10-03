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

  window.Site = Site;
})();
