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

  // Prototype recordings: story captions follow the clip, it plays from the start when it
  // scrolls into view and pauses when it leaves. Reduced-motion visitors press play themselves.
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.cs-reel').forEach(function (reel) {
    var video = reel.querySelector('video');
    var cap = reel.querySelector('.cs-reel-cap');
    var btn = reel.querySelector('.cs-reel-toggle');
    var bar = reel.querySelector('.cs-reel-progress i');
    var cues = reel.dataset.captions.split(';').map(function (c) {
      var p = c.split('|');
      return { t: +p[0], text: p[1] };
    });
    var shown = null, userPaused = reduceMotion;

    function caption() {
      var text = cues[0].text;
      cues.forEach(function (c) { if (video.currentTime >= c.t) text = c.text; });
      if (video.duration) bar.style.width = (video.currentTime / video.duration * 100) + '%';
      if (text === shown) return;
      shown = text;
      cap.classList.remove('on');
      void cap.offsetWidth;
      cap.textContent = text;
      cap.classList.add('on');
    }
    function sync() {
      var playing = !video.paused;
      btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      btn.setAttribute('aria-label', playing ? 'Pause recording' : 'Play recording');
    }
    video.addEventListener('timeupdate', caption);
    video.addEventListener('seeked', caption);
    video.addEventListener('play', sync);
    video.addEventListener('pause', sync);
    btn.addEventListener('click', function () {
      userPaused = !video.paused;
      if (userPaused) video.pause(); else video.play();
    });
    caption();
    sync();

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          if (!userPaused && video.paused) { video.currentTime = 0; video.play().catch(function () {}); }
        } else if (!video.paused) {
          video.pause();
        }
      }, { threshold: 0.5 }).observe(reel);
    } else if (!userPaused) {
      video.play().catch(function () {});
    }
  });
})();
