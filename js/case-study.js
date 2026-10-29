/* Case studies: table-of-contents scroll spy, back-to-top button, before/after switch,
   "see more research" toggle and annotated-screenshot highlighting. */
(function () {
  'use strict';

  var tocLinks = document.querySelectorAll('.cstoc a[href^="#"]');
  var IDS = Array.prototype.map.call(tocLinks, function (a) { return a.getAttribute('href').slice(1); });
  var mark = document.querySelector('.toc-mark');

  var active = null;   // nothing is highlighted until the reader reaches the first section
  var lockId = null, lockUntil = 0;
  var raf = null;

  function renderToc() {
    tocLinks.forEach(function (a) {
      var on = a.getAttribute('href').slice(1) === active;
      a.setAttribute('aria-current', on ? 'location' : 'false');
      a.style.fontWeight = on ? '800' : '600';
      a.style.color = on ? 'var(--ink)' : 'var(--ink-muted)';
    });
    if (mark) {
      mark.style.top = (Math.max(0, IDS.indexOf(active)) * 36) + 'px';
      mark.style.opacity = active ? '1' : '0';
    }
  }

  function onScroll() {
    if (raf) return;
    raf = requestAnimationFrame(function () {
      raf = null;
      var next = null;
      var line = window.innerHeight * 0.4;
      IDS.forEach(function (id) {
        var el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top < line) next = id;
      });
      var doc = document.documentElement;
      if (window.innerHeight + window.scrollY >= doc.scrollHeight - 8) next = IDS[IDS.length - 1];
      if (lockId && Date.now() < lockUntil) {
        next = lockId;
        lockUntil = Math.max(lockUntil, Date.now() + 160);
      } else {
        lockId = null;
      }
      if (next !== active) { active = next; renderToc(); }
      Site.show('back-to-top', window.scrollY > 600);
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  renderToc();
  setTimeout(onScroll, 80);

  var researchOpen = false;

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t.closest) return;

    // Before / after switch
    var tab = t.closest('.ba2-tab');
    if (tab) {
      var after = tab.getAttribute('data-v') === 'after';
      var ba = tab.closest('.ba2');
      ba.classList.toggle('on', after);
      ba.querySelectorAll('.ba2-tab').forEach(function (b) {
        b.setAttribute('aria-pressed', String((b.getAttribute('data-v') === 'after') === after));
      });
      return;
    }

    // "See more research" toggle
    var more = t.closest('.rmore-btn');
    if (more) {
      researchOpen = !researchOpen;
      more.setAttribute('aria-expanded', String(researchOpen));
      more.firstChild.nodeValue = (researchOpen ? '▾ Hide' : '▸ See') + more.firstChild.nodeValue.replace(/^\S+ \S+/, '');
      Site.show('research-more', researchOpen);
      return;
    }

    // Table-of-contents jump: lock the highlight on the clicked section while scrolling there
    var a = t.closest('.cstoc a[href^="#"]');
    if (a) {
      var id = a.getAttribute('href').slice(1);
      var el = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      lockId = id;
      lockUntil = Date.now() + 900;
      active = id;
      renderToc();
      window.scrollTo({ top: Math.max(0, el.getBoundingClientRect().top + window.scrollY - 96), behavior: 'smooth' });
      try { history.replaceState(null, '', '#' + id); } catch (e2) {}
    }
  });

  // Annotated screenshots: hovering or focusing a pin or note highlights its partner
  function highlight(e) {
    var box = e.target.closest && e.target.closest('.anno');
    document.querySelectorAll('.anno [data-n].hl').forEach(function (x) {
      if (!box || !box.contains(x)) x.classList.remove('hl');
    });
    if (!box) return;
    var t = e.target.closest('[data-n]');
    var n = t ? t.getAttribute('data-n') : '';
    box.querySelectorAll('[data-n]').forEach(function (x) {
      x.classList.toggle('hl', x.getAttribute('data-n') === n);
    });
  }
  document.addEventListener('mouseover', highlight);
  document.addEventListener('focusin', highlight);

  // Final design viewer: the frame scrolls to a callout's area when its card is picked, and the
  // "Scroll" hint fades once the visitor scrolls (or isn't needed)
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.cs-view').forEach(function (view) {
    var shot = view.querySelector('.cs-view-shot');
    var frame = view.querySelector('.cs-view-frame');
    function fits() { shot.classList.toggle('fits', frame.scrollHeight <= frame.clientHeight + 4); }
    frame.addEventListener('scroll', function () { shot.classList.add('scrolled'); }, { passive: true });
    window.addEventListener('resize', fits);
    var img = frame.querySelector('img');
    if (img.complete) fits(); else img.addEventListener('load', fits);
    function go(card) {
      var box = view.querySelector('.cs-co-box[data-n="' + card.getAttribute('data-n') + '"]');
      if (box) frame.scrollTo({ top: Math.max(0, box.offsetTop - 16), behavior: calm ? 'auto' : 'smooth' });
    }
    view.querySelectorAll('.cs-view-cards .anno-note').forEach(function (card) {
      card.addEventListener('click', function () { go(card); });
      card.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(card); }
      });
    });
  });
  // a panel hidden on load measures as zero, so re-check when the switch shows it
  document.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.cs-viewer .ba2-tab')) return;
    setTimeout(function () { window.dispatchEvent(new Event('resize')); }, 0);
  });

  // looping prototype recordings stay still for visitors who prefer reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('video[autoplay]').forEach(function (v) {
      v.removeAttribute('autoplay');
      v.pause();
    });
  }
})();
