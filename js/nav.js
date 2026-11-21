// nav.js — mobile menu toggle + current-page highlight. Loaded with defer on every page.
(function () {
  var btn = document.querySelector('.nav-toggle'), nav = document.getElementById('site-nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); }
    });
    nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') { nav.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); } });
  }
  var here = location.pathname.replace(/\.html$/, '');
  document.querySelectorAll('.header-nav a').forEach(function (a) {
    if (a.getAttribute('href').replace(/\.html$/, '') === here) a.setAttribute('aria-current', 'page');
  });
})();
