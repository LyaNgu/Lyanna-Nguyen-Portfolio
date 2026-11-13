/* Cozy UI sounds + an Animal Crossing-style talking voice.
   UI sound effects by lolurio (CC BY 4.0), https://lolurio.itch.io/
   Kept minimal: only the knock-on-the-door greeting makes sound. Nothing plays
   until the visitor interacts. */
(function () {
  'use strict';
  var AC = window.AudioContext || window.webkitAudioContext;
  var ctx = null, buffers = {}, loading = false;
  var FILES = ['close'];
  var VOL = { close: .25 };
  var on = true;

  function base() { return (document.querySelector('script[src*="sfx.js"]').getAttribute('src') || '').replace(/js\/sfx\.js.*$/, ''); }
  function init() {
    if (ctx || !AC) return;
    ctx = new AC();
    if (loading) return; loading = true;
    var root = base();
    FILES.forEach(function (n) {
      fetch(root + 'assets/audio/' + n + '.mp3').then(function (r) { return r.arrayBuffer(); })
        .then(function (d) { return new Promise(function (ok, no) { ctx.decodeAudioData(d, ok, no); }); })
        .then(function (b) { buffers[n] = b; }).catch(function () {});
    });
  }
  function ready() { if (!on || !ctx) return false; if (ctx.state === 'suspended') ctx.resume(); return true; }

  function play(name, vol, rate) {
    if (!ready() || !buffers[name]) return;
    var s = ctx.createBufferSource(), g = ctx.createGain();
    s.buffer = buffers[name]; s.playbackRate.value = rate || 1;
    g.gain.value = vol == null ? (VOL[name] || .3) : vol;
    s.connect(g).connect(ctx.destination); s.start();
  }

  /* Animalese-style voice: each letter becomes a tiny pitched "blip" whose
     pitch is set by the letter, vowels a little higher, run through a soft
     vocal-ish filter so it sounds like chatter rather than beeps. */
  var lastTalk = 0;
  /* Cute, wholesome voice: a soft rounded "bloop" per syllable, sung on a
     major pentatonic scale (so every run of notes sounds friendly, never
     dissonant), with a tiny upward chirp and no buzzy edges. */
  var SCALE = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.5];   // C5 D5 E5 G5 A5 C6
  function talk(ch) {
    if (!ready() || !/[a-z0-9]/i.test(ch)) return;
    var now = ctx.currentTime;
    if (now - lastTalk < .085) return;
    lastTalk = now;
    var c = ch.toLowerCase(), vowel = 'aeiouy'.indexOf(c) > -1;
    var n = (c.charCodeAt(0) * 5) % 4 + (vowel ? 2 : 0);          // vowels sit a little higher
    var f = SCALE[n];
    var o = ctx.createOscillator(), o2 = ctx.createOscillator();
    var g = ctx.createGain(), g2 = ctx.createGain(), lp = ctx.createBiquadFilter();
    o.type = 'sine'; o2.type = 'sine';
    o.frequency.setValueAtTime(f * .96, now); o.frequency.exponentialRampToValueAtTime(f * 1.02, now + .05);
    o2.frequency.setValueAtTime(f * 2 * .96, now); o2.frequency.exponentialRampToValueAtTime(f * 2 * 1.02, now + .05);
    g2.gain.value = .18;                                           // a hint of overtone for warmth
    lp.type = 'lowpass'; lp.frequency.value = 2600;
    g.gain.setValueAtTime(0, now);
    g.gain.linearRampToValueAtTime(.075, now + .014);
    g.gain.exponentialRampToValueAtTime(.001, now + .13);
    o.connect(lp); o2.connect(g2).connect(lp); lp.connect(g).connect(ctx.destination);
    o.start(now); o2.start(now); o.stop(now + .15); o2.stop(now + .15);
  }

  /* Soft knock: two muffled wooden taps, synthesised (a short low thump plus a
     filtered tick of noise), quiet enough to feel like knuckles on a door. */
  function knock() {
    if (!ready()) return;
    var t0 = ctx.currentTime + .02;
    [0, .19].forEach(function (d, i) {
      var t = t0 + d, o = ctx.createOscillator(), og = ctx.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(i ? 200 : 185, t); o.frequency.exponentialRampToValueAtTime(95, t + .09);
      og.gain.setValueAtTime(0, t); og.gain.linearRampToValueAtTime(.22, t + .004); og.gain.exponentialRampToValueAtTime(.001, t + .12);
      o.connect(og).connect(ctx.destination); o.start(t); o.stop(t + .14);
      var n = ctx.createBuffer(1, Math.floor(ctx.sampleRate * .05), ctx.sampleRate), dta = n.getChannelData(0);
      for (var k = 0; k < dta.length; k++) dta[k] = (Math.random() * 2 - 1) * Math.pow(1 - k / dta.length, 3);
      var src = ctx.createBufferSource(), lp = ctx.createBiquadFilter(), ng = ctx.createGain();
      src.buffer = n; lp.type = 'lowpass'; lp.frequency.value = 900; ng.gain.value = .12;
      src.connect(lp).connect(ng).connect(ctx.destination); src.start(t);
    });
  }

  window.Sfx = { play: play, talk: talk, knock: knock };

  /* Phones (especially iPhone Safari) only let sound start inside a real tap:
     on every tap until audio is running, resume it and play one silent frame,
     which unlocks Web Audio on iOS and Android alike. */
  var UNLOCK = ['touchend', 'click', 'keydown', 'pointerup'];
  function unlock() {
    init();
    if (!ctx) return;
    if (ctx.state !== 'running') { try { ctx.resume(); } catch (e) {} }
    try {
      var b = ctx.createBuffer(1, 1, ctx.sampleRate || 22050), s = ctx.createBufferSource();
      s.buffer = b; s.connect(ctx.destination); s.start(0);
    } catch (e) {}
    if (ctx.state === 'running') UNLOCK.forEach(function (t) { window.removeEventListener(t, unlock, true); });
  }
  function wire() {
    window.addEventListener('pointerdown', init, { once: true, capture: true });
    UNLOCK.forEach(function (t) { window.addEventListener(t, unlock, true); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
