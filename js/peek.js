/* Case study sneak peek: a three-scene story carousel. Each scene plays its CSS animation once;
   visitors move on with the arrows or dots. The first scene waits until the carousel is on
   screen, and nothing moves for visitors who prefer reduced motion. */
(function () {
  'use strict';

  var root = document.querySelector('.pk');
  if (!root) return;

  var slides = root.querySelectorAll('.pk-slide');
  var dotsBox = root.querySelector('.pk-dots');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var current = 0, started = false;

  // Scene 2: real channel names from the club's Discord, padded with blank rows to 41.
  var NAMES = ['welcome', 'general-info', 'rules', 'assign-roles', 'modmail', 'general-qna',
    'flash-sale-info', 'flash-sale-announcements', 'listings', 'dino-hunt-info', 'sticker-drop-info',
    'sticker-intros', 'sticker-drop-notifs', 'sticker-found', 'sticker-found-discussion', 'general',
    'new-home-photos', 'announcements'];
  var chans = root.querySelector('.pk-chans');
  if (chans) {
    var seed = 7;
    var rand = function () { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
    // channels land in a scattered order, so the flood feels chaotic rather than row by row
    var order = [];
    for (var k = 0; k < 41; k++) order.push(k);
    order.sort(function () { return rand() - .5; });
    for (var i = 0; i < 41; i++) {
      var el = document.createElement('span');
      var name = NAMES[i];
      el.className = 'pk-chan' + (name ? (rand() > .6 ? ' unread' : '') : ' skel');
      if (name) {
        el.innerHTML = '<i>#</i>' + name + (rand() > .75 ? '<em>' + (1 + Math.floor(rand() * 12)) + '</em>' : '');
      }
      el.style.left = (2 + (i % 5) * 19.5 + rand() * 4) + '%';
      el.style.top = (3 + Math.floor(i / 5) * 11 + rand() * 4) + '%';
      el.style.setProperty('--r', ((rand() - .5) * 8).toFixed(1) + 'deg');
      el.style.animationDelay = (order[i] * 0.1).toFixed(2) + 's';
      chans.appendChild(el);
    }
  }

  slides.forEach(function (s, i) {
    var b = document.createElement('button');
    b.type = 'button';
    b.setAttribute('aria-label', 'Scene ' + s.getAttribute('aria-label'));
    b.addEventListener('click', function () { go(i); });
    dotsBox.appendChild(b);
  });
  var dots = dotsBox.querySelectorAll('button');

  function go(i) {
    current = (i + slides.length) % slides.length;
    slides.forEach(function (s, k) {
      var on = k === current;
      s.classList.toggle('is-active', on);
      s.classList.remove('play');
      s.setAttribute('aria-hidden', on ? 'false' : 'true');
      dots[k].setAttribute('aria-current', on ? 'true' : 'false');
    });
    showPage('gs');
    void slides[current].offsetWidth;          // restart the scene's animations
    if (!reduced) slides[current].classList.add('play');
    countDown(slides[current]);
  }

  // Scene 3: count the channels down to one page
  var countRaf = null;
  function countDown(slide) {
    cancelAnimationFrame(countRaf);
    var num = slide.querySelector('.pk-num');
    if (!num) return;
    var from = +num.dataset.from, delay = 1000, dur = 1300, t0 = null;
    if (reduced || !started) { num.textContent = '1'; return; }
    num.textContent = from;
    countRaf = requestAnimationFrame(function step(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(Math.max((t - t0 - delay) / dur, 0), 1);
      num.textContent = Math.round(from - (from - 1) * (1 - Math.pow(1 - k, 3)));
      if (k < 1) countRaf = requestAnimationFrame(step);
    });
  }

  // Scene 3: the Flash Sales card swaps the big screen between the two pages
  var sol = root.querySelector('.pk-sol'), swap = root.querySelector('.pk-fs');
  function showPage(page) {
    if (!sol) return;
    sol.dataset.page = page;
    swap.setAttribute('aria-pressed', page === 'fs' ? 'true' : 'false');
    swap.setAttribute('aria-label', page === 'fs' ? 'Back to the Getting Started page' : 'Show the Flash Sales page');
  }
  if (swap) swap.addEventListener('click', function () { showPage(sol.dataset.page === 'fs' ? 'gs' : 'fs'); });

  root.querySelector('.pk-arrow.prev').addEventListener('click', function () { go(current - 1); });
  root.querySelector('.pk-arrow.next').addEventListener('click', function () { go(current + 1); });

  // play the first scene once the carousel scrolls into view
  function start() { if (!started) { started = true; root.classList.add('is-live'); go(current); } }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { start(); io.disconnect(); }
    }, { threshold: 0.4 });
    io.observe(root);
  } else {
    start();
  }

  go(0);
})();
