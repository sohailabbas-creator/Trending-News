/* sohailabbas.site — shared behaviour (extracted from the per-page inline script).
   Only the mobile navigation toggle lives here; each tool keeps its own script inline
   in its page so that a tool page is fully self-contained. */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('nav-toggle');
    var nav = document.getElementById('site-nav');
    if (!btn || !nav) return;
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });
})();
