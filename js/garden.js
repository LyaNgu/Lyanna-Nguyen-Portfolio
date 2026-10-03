/* Design Garden: scroll reveal and category filter tabs. */
(function () {
  'use strict';

  Site.initReveal();

  var tabs = document.querySelectorAll('[data-action="filter"]');
  var categories = [];
  tabs.forEach(function (t) {
    var k = t.getAttribute('data-filter');
    if (k !== 'all') categories.push(k);
  });

  Site.on('filter', function (e, btn) {
    var pick = btn.getAttribute('data-filter');
    tabs.forEach(function (t) {
      var on = t === btn;
      t.setAttribute('aria-pressed', String(on));
      t.style.background = on ? 'var(--wood)' : 'var(--surface-raised)';
      t.style.color = on ? 'var(--on-wood)' : 'var(--ink)';
    });
    categories.forEach(function (k) {
      Site.show('cat-' + k, pick === 'all' || pick === k);
    });
  });
})();
