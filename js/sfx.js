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
  function talk(ch) {
    if (!ready() || !/[a-z0-9]/i.test(ch)) return;
    var now = ctx.currentTime;
    if (now - lastTalk < .055) return;
    lastTalk = now;
    var c = ch.toLowerCase(), vowel = 'aeiouy'.indexOf(c) > -1;
    var idx = (c.charCodeAt(0) * 7) % 12;
    var f = 440 * Math.pow(2, idx / 24) * (vowel ? 1.18 : 1) * (0.97 + Math.random() * .06);
    var o = ctx.createOscillator(), o2 = ctx.createOscillator();
    var bp = ctx.createBiquadFilter(), g = ctx.createGain();
    o.type = 'triangle'; o2.type = 'square';
    o.frequency.setValueAtTime(f * 1.06, now); o.frequency.exponentialRampToValueAtTime(f * .94, now + .07);
    o2.frequency.setValueAtTime(f * 2, now); o2.frequency.exponentialRampToValueAtTime(f * 1.86, now + .07);
    var g2 = ctx.createGain(); g2.gain.value = .1;
    bp.type = 'bandpass'; bp.frequency.value = vowel ? 1700 : 1300; bp.Q.value = 1.2;
    g.gain.setValueAtTime(0, now);
    g.gain.linearRampToValueAtTime(.09, now + .01);
    g.gain.exponentialRampToValueAtTime(.001, now + .075);
    o.connect(bp); o2.connect(g2).connect(bp); bp.connect(g).connect(ctx.destination);
    o.start(now); o2.start(now); o.stop(now + .09); o2.stop(now + .09);
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

  function wire() {
    ['pointerdown', 'keydown'].forEach(function (t) { window.addEventListener(t, init, { once: true, capture: true }); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire);
  else wire();
})();
