// 소로롱 초안 공통 스크립트
(function () {
  // 등장
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });

  // 숫자 카운트
  var cio = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target, to = parseFloat(el.dataset.count), dec = (el.dataset.count.split('.')[1] || '').length;
      var t0 = performance.now(), dur = 1400;
      (function tick(t) {
        var p = Math.min(1, (t - t0) / dur), k = 1 - Math.pow(1 - p, 3);
        el.textContent = (to * k).toFixed(dec);
        if (p < 1) requestAnimationFrame(tick);
      })(t0);
      cio.unobserve(el);
    });
  }, { threshold: 0.5 });
  document.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });

  // 헤더 스크롤
  var hdr = document.querySelector('[data-header]');
  if (hdr) {
    var onS = function () { hdr.classList.toggle('scrolled', window.scrollY > 40); };
    addEventListener('scroll', onS, { passive: true }); onS();
  }

  // 모바일 메뉴
  var btn = document.querySelector('[data-menu-btn]'), nav = document.querySelector('[data-nav]');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });

  // 고객사 흐름 복제
  document.querySelectorAll('.marquee__track').forEach(function (tr) { tr.innerHTML += tr.innerHTML; });

  // 초안 전환 바
  var here = location.pathname.split('/').pop();
  var bar = document.createElement('nav'); bar.className = 'draftbar'; bar.setAttribute('aria-label', '초안 전환');
  [['a.html', 'A안'], ['b.html', 'B안'], ['c.html', 'C안'], ['d.html', 'D안'], ['e.html', 'E안'], ['f.html', 'F안']].forEach(function (d) {
    var a = document.createElement('a'); a.href = d[0]; a.textContent = d[1]; if (here === d[0]) a.className = 'on'; bar.appendChild(a);
  });
  document.body.appendChild(bar);
})();
