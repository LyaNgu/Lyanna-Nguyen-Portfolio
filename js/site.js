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


  // Navbar email pill: copy the address, with a short "Copied!" confirmation
  function initCopy() {
    document.querySelectorAll('[data-copy]').forEach(function (btn) {
      var label = btn.querySelector('.nav-email-t'), text = label ? label.textContent : '';
      btn.addEventListener('click', function () {
        var done = function () {
          btn.classList.add('copied'); if (label) label.textContent = 'Copied!';
          setTimeout(function () { btn.classList.remove('copied'); if (label) label.textContent = text; }, 1600);
        };
        var v = btn.getAttribute('data-copy');
        if (navigator.clipboard) navigator.clipboard.writeText(v).then(done, function () { location.href = 'mailto:' + v; });
        else location.href = 'mailto:' + v;
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCopy);
  else initCopy();


  // Nav pill: a soft highlight slides to whichever link is hovered or focused
  function initNavHl() {
    var nav = document.querySelector('.sitenav .topnav'), hl = nav && nav.querySelector('.nav-hl');
    if (!hl) return;
    function to(a) { if (!a) { nav.classList.remove('has-hl'); return; } hl.style.left = a.offsetLeft + 'px'; hl.style.width = a.offsetWidth + 'px'; nav.classList.add('has-hl'); }
    nav.querySelectorAll('.navlinks').forEach(function (a) {
      a.addEventListener('mouseenter', function () { to(a); });
      a.addEventListener('focus', function () { to(a); });
      a.addEventListener('blur', function () { to(null); });
    });
    nav.addEventListener('mouseleave', function () { to(null); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initNavHl);
  else initNavHl();


  // Nav pill: the gold block sits on the current page and glides to a clicked link before the page changes
  function initNavCur() {
    var nav = document.querySelector('.sitenav .topnav'), cur = nav && nav.querySelector('.nav-cur');
    if (!cur) return;
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function place(a, anim) {
      if (!a) return;
      if (!anim) cur.classList.add('no-anim');
      cur.style.left = a.offsetLeft + 'px'; cur.style.width = a.offsetWidth + 'px'; nav.classList.add('has-cur');
      if (!anim) { void cur.offsetWidth; cur.classList.remove('no-anim'); }
      else { cur.classList.remove('squish'); void cur.offsetWidth; cur.classList.add('squish'); }
    }
    function current() { return nav.querySelector('.navlinks[aria-current="page"]'); }
    function settle() { place(current(), false); }
    settle();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(settle);
    window.addEventListener('load', settle);
    window.addEventListener('resize', settle);
    // Home page: the block follows the scroll, landing on Works while Selected work is on screen
    var work = document.getElementById('work'), homeLink = nav.querySelector('.navlinks[href="#top"]'), workLink = nav.querySelector('.navlinks[href="#work"]');
    if (work && homeLink && workLink && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        var on = es[0].isIntersecting || es[0].boundingClientRect.top < 0, want = on ? workLink : homeLink, was = current();
        if (want === was) return;
        if (was) was.removeAttribute('aria-current');
        want.setAttribute('aria-current', 'page'); place(want, true);
      }, { rootMargin: '-35% 0px -45% 0px' }).observe(work);
    }
    nav.querySelectorAll('.navlinks').forEach(function (a) {
      a.addEventListener('click', function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
        var was = current();
        if (a === was) return;
        if (was) was.removeAttribute('aria-current');
        a.setAttribute('aria-current', 'page');
        place(a, true);
        var href = a.getAttribute('href');
        // same-page jumps and new-tab links just keep the block where it landed
        if (a.target === '_blank') { setTimeout(function () { a.removeAttribute('aria-current'); if (was) was.setAttribute('aria-current', 'page'); place(was, true); }, 900); return; }
        if (href.charAt(0) === '#') return;
        if (reduce) return;
        e.preventDefault();
        setTimeout(function () { location.href = href; }, 380);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initNavCur);
  else initNavCur();

  window.Site = Site;
})();
