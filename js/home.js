/* Home page: opening animation, knock-on-the-door greeting and night-time fireflies. */
(function () {
  'use strict';

  var LOADER_KEY = 'ln_farm_loader_seen';
  var LINES = [
    "Oh! A visitor! Hi, I'm Lyanna Nguyen, welcome to my little farm.",
    "I'm a product designer and UX researcher. I enjoy chatting with people and creating designs that solve their problems!",
    'Feel free to wander around and explore, make yourself at home!'
  ];

  Site.initReveal();

  /* ---------- Opening animation (first visit per browser session) ---------- */
  var loaderTimer;
  function hideLoader() {
    clearTimeout(loaderTimer);
    Site.show('loader', false);
  }
  (function () {
    var seen = false;
    try { seen = sessionStorage.getItem(LOADER_KEY) === '1'; } catch (e) {}
    if (seen || Site.reducedMotion) return;
    Site.show('loader', true);
    loaderTimer = setTimeout(hideLoader, 3550);
    try { sessionStorage.setItem(LOADER_KEY, '1'); } catch (e) {}
  })();
  Site.on('skip-loader', hideLoader);

  /* ---------- Knock on the door → Lyanna says hello ---------- */
  var house = document.querySelector('.clickhouse');
  var door = house.querySelector('.door');
  var doorPanel = house.querySelector('.doorpanel');
  var girl = house.querySelector('.greetgirl .emerge > div');
  var typedEl = document.querySelector('.dlg-typed');
  var ghostEl = document.querySelector('.dlg-ghost');   // invisible longest line: every line gets the same box size
  var LONGEST = LINES.reduce(function (a, b) { return b.length > a.length ? b : a; });

  var phase = 'idle';   // idle → knocking → open → greet
  var line = 0;
  var chars = 0;
  var jump = '';
  var typer, knockT1, knockT2;

  function bounce() {
    jump = jump === 'jumpA' ? 'jumpB' : 'jumpA';
    girl.className = jump;
  }

  function render() {
    var greeted = phase === 'greet';
    var text = LINES[line];
    var typedDone = chars >= text.length;
    var lastLine = line === LINES.length - 1;

    door.classList.toggle('shake', phase === 'knocking');
    doorPanel.style.transform = (phase === 'open' || greeted) ? 'perspective(300px) rotateY(-80deg)' : 'none';
    house.setAttribute('aria-label', greeted ? 'Close the door and knock again' : 'Click to knock on the door');

    Site.show('knocking', phase === 'knocking');
    Site.show('knock-hint', phase === 'idle');
    Site.show('greeted', greeted);
    Site.show('dialog-next', greeted && !(lastLine && typedDone));
    Site.show('dialog-choices', greeted && lastLine && typedDone);
    typedEl.textContent = text.slice(0, Math.min(chars, text.length));
    ghostEl.textContent = LONGEST + '\u258C';
    if (greeted) reserveFooter();
  }

  // The last line swaps Next for two buttons; reserve their height on every line so the box never resizes
  var footer = document.querySelector('.dlg-text > div');
  var choices = document.querySelectorAll('[data-show="dialog-choices"]');
  var nextBtn = document.querySelector('[data-show="dialog-next"]');
  function reserveFooter() {
    var was = Array.prototype.map.call(choices, function (el) { return el.hidden; });
    var nextWas = nextBtn.hidden;
    footer.style.minHeight = '';
    nextBtn.hidden = true;
    choices.forEach(function (el) { el.hidden = false; });
    var withChoices = footer.offsetHeight;
    nextBtn.hidden = false;
    choices.forEach(function (el) { el.hidden = true; });
    var withNext = footer.offsetHeight;
    nextBtn.hidden = nextWas;
    choices.forEach(function (el, i) { el.hidden = was[i]; });
    footer.style.minHeight = Math.max(withChoices, withNext) + 'px';
  }

  function type() {
    clearInterval(typer);
    if (Site.reducedMotion) { chars = LINES[line].length; render(); return; }
    typer = setInterval(function () {
      if (chars >= LINES[line].length) { clearInterval(typer); return; }
      chars += 2;
      if (window.Sfx) Sfx.talk(LINES[line].charAt(chars - 1));
      render();
    }, 30);
  }

  function reset() {
    clearInterval(typer);
    phase = 'idle'; line = 0; chars = 0;
    render();
  }

  function knock() {
    if (phase === 'greet') { if (window.Sfx) Sfx.play('close'); reset(); return; }
    if (phase !== 'idle') return;
    var fast = Site.reducedMotion;
    phase = 'knocking';
    if (window.Sfx) Sfx.knock();
    render();
    knockT1 = setTimeout(function () { phase = 'open'; render(); }, fast ? 0 : 950);
    knockT2 = setTimeout(function () {
      phase = 'greet'; line = 0; chars = 0; jump = '';
      bounce();
      render();
      type();
    }, fast ? 0 : 1500);
  }

  function next() {
    var full = LINES[line].length;
    if (chars < full) { clearInterval(typer); chars = full; render(); return; }
    if (line < LINES.length - 1) {
      line += 1; chars = 0;
      bounce();
      render();
      type();
    }
  }

  Site.on('knock', knock);
  house.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); knock(); }
  });
  Site.on('dialog-next', next);
  Site.on('dialog-advance', function (e) {
    if (e.target.closest('.dlg-x, a, button')) return;
    next();
  });
  Site.on('close-dialog', function () { if (phase === 'greet' && window.Sfx) Sfx.play('close'); reset(); });   // also used by the "Start the tour" / "Just the resume" links


  /* ---------- Work covers: slowly scroll each screenshot top to bottom and back ---------- */
  (function () {
    if (Site.reducedMotion || !Element.prototype.animate) return;
    var imgs = document.querySelectorAll('.wc-win-scr img, .wc-lc-view img.wc-lc-scroll');
    var anims = [];
    function start() {
      anims.forEach(function (a) { a.cancel(); }); anims = [];
      imgs.forEach(function (img, i) {
        var box = img.parentElement, dist = img.offsetHeight - box.clientHeight;
        if (!img.complete || dist <= 0) return;
        var secs = 32;   // every cover scrolls in step: same speed and timing, top and bottom together
        var a = img.animate([
          { transform: 'translateY(0)', offset: 0 }, { transform: 'translateY(0)', offset: .06 },
          { transform: 'translateY(' + -dist + 'px)', offset: .94 }, { transform: 'translateY(' + -dist + 'px)', offset: 1 }
        ], { duration: secs * 1000, iterations: Infinity, direction: 'alternate', easing: 'ease-in-out' });
        a.startTime = 0;   // shared timeline, so they stay in sync even if images load at different times
        anims.push(a);
        var card = img.closest('.workcard');
        if (card && !card._wcHover) {
          card._wcHover = true;
          card.addEventListener('mouseenter', function () { anims.forEach(function (x) { if (card.contains(x.effect.target)) x.pause(); }); });
          card.addEventListener('mouseleave', function () { anims.forEach(function (x) { if (card.contains(x.effect.target)) x.play(); }); });
        }
      });
    }
    imgs.forEach(function (img) { if (!img.complete) img.addEventListener('load', start, { once: true }); });
    window.addEventListener('load', start);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(start, 200); });
    start();
  })();

  /* ---------- Fireflies scatter away from the cursor ---------- */
  var night = document.querySelector('[data-night]');
  if (night) {
    var RADIUS = 140, PUSH = 34, raf = null;
    var flies = night.querySelectorAll('.ffw');
    night.addEventListener('mousemove', function (e) {
      if (raf) return;
      var x = e.clientX, y = e.clientY;
      raf = requestAnimationFrame(function () {
        raf = null;
        flies.forEach(function (el) {
          var r = el.getBoundingClientRect();
          var dx = (r.left + 2.5) - x, dy = (r.top + 2.5) - y;
          var d = Math.hypot(dx, dy);
          if (d < RADIUS) {
            var f = (1 - d / RADIUS) * PUSH / Math.max(d, 1);
            el.style.transform = 'translate(' + (dx * f).toFixed(1) + 'px,' + (dy * f).toFixed(1) + 'px)';
            el.classList.add('near');
          } else if (el.style.transform) {
            el.style.transform = '';
            el.classList.remove('near');
          }
        });
      });
    });
    night.addEventListener('mouseleave', function () {
      flies.forEach(function (el) { el.style.transform = ''; el.classList.remove('near'); });
    });
  }
})();
