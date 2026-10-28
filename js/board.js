/* Town bulletin board: pick up a note (drag, or arrow keys when focused) and pin it anywhere.
   Positions are remembered per visitor in localStorage, and "Tidy up" puts everything back. */
(function () {
  'use strict';

  var board = document.querySelector('.bb-board');
  if (!board) return;
  var notes = Array.prototype.slice.call(board.querySelectorAll('.bb-note'));
  var tidy = document.querySelector('.bb-tidy');
  var narrow = window.matchMedia('(max-width: 700px)');
  var KEY = 'ln_board_v2';   // bump when the default layout changes
  var top = 10;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(all) {
    try { localStorage.setItem(KEY, JSON.stringify(all)); } catch (e) {}
  }
  var saved = load();
  function layout() { return narrow.matches ? 'narrow' : 'wide'; }

  function place(note, x, y, r) {
    note.style.left = x + '%';
    note.style.top = y + '%';
    if (r !== undefined) note.style.setProperty('--r', r + 'deg');
  }
  function restore() {
    var mine = saved[layout()] || {};
    notes.forEach(function (n, i) {
      n.style.left = ''; n.style.top = '';
      var p = mine[i];
      if (p) place(n, p.x, p.y, p.r);
    });
  }
  function remember(note) {
    var i = notes.indexOf(note), l = layout();
    saved[l] = saved[l] || {};
    saved[l][i] = {
      x: parseFloat(note.style.left), y: parseFloat(note.style.top),
      r: parseFloat(note.style.getPropertyValue('--r'))
    };
    save(saved);
  }

  // keep a note fully on the board; returns % position
  function clamp(note, leftPx, topPx) {
    var b = board.getBoundingClientRect();
    var maxL = b.width - note.offsetWidth, maxT = b.height - note.offsetHeight;
    return {
      x: Math.max(0, Math.min(leftPx, maxL)) / b.width * 100,
      y: Math.max(0, Math.min(topPx, maxT)) / b.height * 100
    };
  }

  function drop(note) {
    note.classList.remove('is-held');
    // re-pinned notes settle at a fresh slight tilt
    note.style.setProperty('--r', (Math.round((Math.random() * 8 - 4) * 10) / 10) + 'deg');
    note.classList.remove('is-dropped');
    void note.offsetWidth;
    note.classList.add('is-dropped');
    remember(note);
  }

  notes.forEach(function (note) {
    var start = null, dragged = false;

    note.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      start = { x: e.clientX, y: e.clientY, left: note.offsetLeft, top: note.offsetTop, id: e.pointerId };
      dragged = false;
    });

    note.addEventListener('pointermove', function (e) {
      if (!start || e.pointerId !== start.id) return;
      var dx = e.clientX - start.x, dy = e.clientY - start.y;
      if (!dragged) {
        if (Math.abs(dx) + Math.abs(dy) < 6) return;   // ignore tiny jitters
        dragged = true;
        note.setPointerCapture(e.pointerId);
        note.style.zIndex = ++top;
        note.classList.remove('is-dropped');
        note.classList.add('is-held');
      }
      var p = clamp(note, start.left + dx, start.top + dy);
      place(note, p.x, p.y);
    });

    function end(e) {
      if (!start || e.pointerId !== start.id) return;
      start = null;
      if (dragged) drop(note);
    }
    note.addEventListener('pointerup', end);
    note.addEventListener('pointercancel', end);

    // keyboard: arrow keys nudge the focused note (Shift for bigger steps)
    note.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 40 : 12, dx = 0, dy = 0;
      if (e.key === 'ArrowLeft') dx = -step;
      else if (e.key === 'ArrowRight') dx = step;
      else if (e.key === 'ArrowUp') dy = -step;
      else if (e.key === 'ArrowDown') dy = step;
      else return;
      e.preventDefault();
      note.style.zIndex = ++top;
      var p = clamp(note, note.offsetLeft + dx, note.offsetTop + dy);
      place(note, p.x, p.y);
      remember(note);
    });
  });

  tidy.addEventListener('click', function () {
    saved = {};
    save(saved);
    notes.forEach(function (n) {
      n.style.left = ''; n.style.top = ''; n.style.zIndex = '';
      n.style.removeProperty('--r');
    });
    // inline --r from the markup was cleared above; put the originals back
    notes.forEach(function (n) { n.style.setProperty('--r', n.dataset.r); });
  });
  notes.forEach(function (n) { n.dataset.r = n.style.getPropertyValue('--r'); });

  narrow.addEventListener('change', restore);
  restore();
})();
