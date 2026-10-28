/* Home page: opening animation, knock-on-the-door greeting, mailbox and night-time fireflies. */
(function () {
  'use strict';

  var LOADER_KEY = 'ln_farm_loader_seen';
  var LINES = [
    "Oh! A visitor! Hi, I'm Lyanna Nguyen, welcome to my little farm.",
    "I design apps and websites and do UX research, which mostly means asking people lots of questions, then sketching until things click.",
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
    loaderTimer = setTimeout(hideLoader, 3650);
    try { sessionStorage.setItem(LOADER_KEY, '1'); } catch (e) {}
  })();
  Site.on('skip-loader', hideLoader);

  /* ---------- Knock on the door → Lyanna says hello ---------- */
  var house = document.querySelector('.clickhouse');
  var door = house.querySelector('.door');
  var doorPanel = house.querySelector('.doorpanel');
  var girl = house.querySelector('.greetgirl .emerge > div');
  var typedEl = document.querySelector('.dlg-typed');
  var ghostEl = document.querySelector('.dlg-ghost');   // invisible full line that sizes the box up front

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
    house.setAttribute('aria-label', greeted ? 'Close the door and knock again' : 'Knock on the door');

    Site.show('knocking', phase === 'knocking');
    Site.show('knock-hint', phase === 'idle');
    Site.show('greeted', greeted);
    Site.show('dialog-next', greeted && !(lastLine && typedDone));
    Site.show('dialog-choices', greeted && lastLine && typedDone);
    typedEl.textContent = text.slice(0, Math.min(chars, text.length));
    ghostEl.textContent = text + '\u258C';
  }

  function type() {
    clearInterval(typer);
    if (Site.reducedMotion) { chars = LINES[line].length; render(); return; }
    typer = setInterval(function () {
      if (chars >= LINES[line].length) { clearInterval(typer); return; }
      chars += 2;
      render();
    }, 30);
  }

  function reset() {
    clearInterval(typer);
    phase = 'idle'; line = 0; chars = 0;
    render();
  }

  function knock() {
    if (phase === 'greet') { reset(); return; }
    if (phase !== 'idle') return;
    var fast = Site.reducedMotion;
    phase = 'knocking';
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
  Site.on('close-dialog', reset);   // also used by the "Start the tour" / "Just the resume" links

  /* ---------- Mailbox ---------- */
  var mailOpen = false;
  var mailBtn = document.querySelector('.mailbtn');
  var envelope = document.querySelector('.mailenv');
  Site.on('toggle-mail', function () {
    mailOpen = !mailOpen;
    mailBtn.setAttribute('aria-expanded', String(mailOpen));
    envelope.classList.toggle('envfly', mailOpen);
    Site.show('mail-closed', !mailOpen);
    Site.show('mail-open', mailOpen);
  });

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
