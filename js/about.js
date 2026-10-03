/* About page: scroll reveals and the "on repeat" song previews. */
(function () {
  'use strict';

  var SONGS = ['3BuaksAZoXoIr8NoxAsIOO', '70cHKK8bHAfJrOGVnfRG9J', '4X5HSbeKuiu3sSa7dP2Z2y', '7H5mEnvW0SjfJEvDUiCG1K'];
  var COVER_PROBE = 'https://image-cdn-ak.spotifycdn.com/image/ab67616d00001e02e6550e9fd374bc1240429aae';

  Site.initReveal();

  var current = -1;
  var blocked = false;   // true when Spotify is unreachable (e.g. blocked by the network)
  var popup = null;

  // If Spotify's CDN is blocked, fall back to vinyl placeholders and pop-out previews.
  var probe = new Image();
  probe.onerror = function () {
    blocked = true;
    Site.show('cover', false);
    render();
  };
  probe.src = COVER_PROBE;

  function render() {
    document.querySelectorAll('[data-action="toggle-song"]').forEach(function (btn) {
      btn.setAttribute('aria-expanded', String(Number(btn.getAttribute('data-song')) === current));
    });
    SONGS.forEach(function (_, i) {
      var on = !blocked && current === i;
      document.querySelectorAll('[data-show="song-' + i + '"]').forEach(function (frame) {
        frame.hidden = !on;
        // Load the player only while it is open so a hidden one never keeps playing.
        if (on && !frame.getAttribute('src')) frame.setAttribute('src', frame.getAttribute('data-src'));
        if (!on && frame.getAttribute('src')) frame.removeAttribute('src');
      });
    });
  }

  function openPopup(id) {
    try { if (popup && !popup.closed) popup.close(); } catch (e) {}
    popup = null;
    try {
      var w = 380, h = 172;
      var left = Math.max(0, (window.screenX || 0) + (window.outerWidth || 1200) - w - 40);
      var top = Math.max(0, (window.screenY || 0) + 120);
      popup = window.open('https://open.spotify.com/embed/track/' + id + '?utm_source=generator&theme=0', 'songpreview',
        'popup=yes,width=' + w + ',height=' + h + ',left=' + left + ',top=' + top);
    } catch (e) {}
    if (!popup) {
      try { window.open('https://open.spotify.com/track/' + id, '_blank', 'noopener'); } catch (e) {}
    }
  }

  Site.on('toggle-song', function (e, btn) {
    var i = Number(btn.getAttribute('data-song'));
    if (blocked && current !== i) openPopup(SONGS[i]);
    current = current === i ? -1 : i;
    render();
  });
})();
