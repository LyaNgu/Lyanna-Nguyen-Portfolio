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

  // Research: the 9 of 15 split wipes in once when the figure scrolls into view
  var flow = document.querySelector('.cs-flow');
  if (flow && 'IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    flow.classList.add('ready');
    var flowIo = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      flow.classList.add('in');
      flowIo.disconnect();
    }, { threshold: 0.4 });
    flowIo.observe(flow);
  }

  // Final design pages: hide the "Scroll to explore" hint once the visitor scrolls a page
  document.querySelectorAll('.cs-page-scroll').forEach(function (el) {
    el.addEventListener('scroll', function () {
      if (el.scrollTop > 40) el.parentNode.classList.add('scrolled');
    }, { passive: true });
  });

  // looping prototype recordings stay still for visitors who prefer reduced motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('video[autoplay]').forEach(function (v) {
      v.removeAttribute('autoplay');
      v.pause();
    });
  }
})();
