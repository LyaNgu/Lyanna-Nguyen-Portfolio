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

  /* ---------- Dialogue sounds (Dialogue SFX by AmbroggioMusic, ambroggiomusic.itch.io) ----------
     Short "voice" blips while Lyanna talks, plus a chirp for hello / next / close. Sounds only play
     after the visitor knocks (a click), and a speaker button beside the close button mutes them. */
  var SOUND_KEY = 'ln_dialogue_sound';
  var soundOn = true;
  try { soundOn = localStorage.getItem(SOUND_KEY) !== 'off'; } catch (e) {}
  var AC = window.AudioContext || window.webkitAudioContext;
  var audio = null, buffers = {};
  function loadSounds() {
    if (audio || !AC) return;
    audio = new AC();
    ['talk-1', 'talk-2', 'hello', 'next', 'close'].forEach(function (name) {
      fetch('assets/audio/' + name + '.mp3')
        .then(function (r) { return r.arrayBuffer(); })
        .then(function (data) { return new Promise(function (ok, no) { audio.decodeAudioData(data, ok, no); }); })
        .then(function (buf) { buffers[name] = buf; })
        .catch(function () {});
    });
  }
  function play(name, rate, volume) {
    if (!soundOn || !audio || !buffers[name]) return;
    if (audio.state === 'suspended') audio.resume();
    var src = audio.createBufferSource(), gain = audio.createGain();
    src.buffer = buffers[name];
    src.playbackRate.value = rate || 1;
    gain.gain.value = volume == null ? 0.35 : volume;
    src.connect(gain).connect(audio.destination);
    src.start();
  }
  var talkTick = 0;
  function talk() {
    // one blip every few letters, with a little pitch variation so it sounds like speech
    if (talkTick++ % 3) return;
    play(talkTick % 2 ? 'talk-1' : 'talk-2', 0.92 + Math.random() * 0.2, 0.28);
  }

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
    house.setAttribute('aria-label', greeted ? 'Close the door and knock again' : 'Knock on the door');

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
      talk();
      render();
    }, 30);
  }

  function reset() {
    clearInterval(typer);
    phase = 'idle'; line = 0; chars = 0;
    render();
  }

  function knock() {
    if (phase === 'greet') { play('close', 1, 0.3); reset(); return; }
    if (phase !== 'idle') return;
    loadSounds();
    var fast = Site.reducedMotion;
    phase = 'knocking';
    render();
    knockT1 = setTimeout(function () { phase = 'open'; render(); }, fast ? 0 : 950);
    knockT2 = setTimeout(function () {
      phase = 'greet'; line = 0; chars = 0; jump = '';
      bounce();
      play('hello', 1, 0.4);
      render();
      type();
    }, fast ? 0 : 1500);
  }

  function next() {
    var full = LINES[line].length;
    if (chars < full) { clearInterval(typer); chars = full; render(); return; }
    if (line < LINES.length - 1) {
      play('next', 1, 0.3);
      line += 1; chars = 0;
      bounce();
      render();
      type();
    }
  }

  var closeBtn = document.querySelector('.dlg-x');
  var soundBtn = document.createElement('button');
  soundBtn.type = 'button';
  soundBtn.className = 'dlg-x dlg-sound';
  soundBtn.innerHTML = '<svg viewBox="0 0 12 12" aria-hidden="true"><path class="spk" d="M1 4h2l3-3v10L3 8H1z"/><path class="on" d="M8 3h1v1H8zM9 4h1v4H9zM8 8h1v1H8zM10 2h1v1h-1zM11 3h1v6h-1zM10 9h1v1h-1z"/><path class="off" d="M8 4h1v1H8zM9 5h1v1H9zM10 6h1v1h-1zM11 7h1v1h-1zM11 4h1v1h-1zM10 5h1v1h-1zM9 6h1v1H9zM8 7h1v1H8z"/></svg>';
  function syncSoundBtn() {
    soundBtn.setAttribute('aria-pressed', String(soundOn));
    soundBtn.setAttribute('aria-label', soundOn ? 'Mute dialogue sounds' : 'Turn on dialogue sounds');
    soundBtn.classList.toggle('muted', !soundOn);
  }
  soundBtn.addEventListener('click', function () {
    soundOn = !soundOn;
    try { localStorage.setItem(SOUND_KEY, soundOn ? 'on' : 'off'); } catch (e) {}
    syncSoundBtn();
    loadSounds();
    if (soundOn) play('next', 1.1, 0.25);
  });
  syncSoundBtn();
  if (closeBtn) closeBtn.parentNode.insertBefore(soundBtn, closeBtn);

  Site.on('knock', knock);
  house.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); knock(); }
  });
  Site.on('dialog-next', next);
  Site.on('dialog-advance', function (e) {
    if (e.target.closest('.dlg-x, a, button')) return;
    next();
  });
  Site.on('close-dialog', function () { if (phase === 'greet') play('close', 1, 0.3); reset(); });   // also used by the "Start the tour" / "Just the resume" links

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
