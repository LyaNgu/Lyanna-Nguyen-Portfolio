/* Case study sneak peek: a three-scene story carousel. Each scene plays its CSS animation,
   then the next one starts. Plays only while on screen, pauses on hover and focus, and stays
   still for visitors who prefer reduced motion. */
(function () {
  'use strict';

  var root = document.querySelector('.pk');
  if (!root) return;

  var slides = root.querySelectorAll('.pk-slide');
  var dotsBox = root.querySelector('.pk-dots');
  var pauseBtn = root.querySelector('.pk-pause');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var current = 0, timer = null, visible = false, hovered = false, paused = reduced;

  // Scene 2: real channel names from the club's Discord, padded with blank rows to 41.
  var NAMES = ['welcome', 'general-info', 'rules', 'assign-roles', 'modmail', 'general-qna',
    'flash-sale-info', 'flash-sale-announcements', 'listings', 'dino-hunt-info', 'sticker-drop-info',
    'sticker-intros', 'sticker-drop-notifs', 'sticker-found', 'sticker-found-discussion', 'general',
    'new-home-photos', 'announcements'];
  var chans = root.querySelector('.pk-chans');
  if (chans) {
    var seed = 7;
    var rand = function () { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
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
      el.style.animationDelay = (i * 0.07).toFixed(2) + 's';
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

  function schedule() {
    clearTimeout(timer);
    if (paused || hovered || !visible) return;
    timer = setTimeout(function () { go(current + 1); }, +slides[current].dataset.dur || 7000);
  }

  function go(i) {
    current = (i + slides.length) % slides.length;
    slides.forEach(function (s, k) {
      var on = k === current;
      s.classList.toggle('is-active', on);
      s.classList.remove('play');
      s.setAttribute('aria-hidden', on ? 'false' : 'true');
      dots[k].setAttribute('aria-current', on ? 'true' : 'false');
    });
    void slides[current].offsetWidth;          // restart the scene's animations
    if (!reduced) slides[current].classList.add('play');
    schedule();
  }

  root.querySelector('.pk-arrow.prev').addEventListener('click', function () { go(current - 1); });
  root.querySelector('.pk-arrow.next').addEventListener('click', function () { go(current + 1); });

  function setPaused(p) {
    paused = p;
    pauseBtn.textContent = p ? 'Play' : 'Pause';
    pauseBtn.setAttribute('aria-pressed', p ? 'true' : 'false');
    root.classList.toggle('is-paused', p);
    schedule();
  }
  pauseBtn.addEventListener('click', function () { setPaused(!paused); });

  root.addEventListener('mouseenter', function () { hovered = true; schedule(); });
  root.addEventListener('mouseleave', function () { hovered = false; schedule(); });
  root.addEventListener('focusin', function () { hovered = true; schedule(); });
  root.addEventListener('focusout', function () { hovered = false; schedule(); });

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      var was = visible;
      visible = entries[0].isIntersecting;
      if (visible && !was) go(current); else schedule();
    }, { threshold: 0.4 }).observe(root);
  } else {
    visible = true;
  }

  setPaused(paused);
  go(0);
})();
