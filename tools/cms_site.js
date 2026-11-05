// 소로롱 사이트 스크립트 (CMS 묶음 · 인라인 스크립트 없이 이 파일 하나)
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };

  // 등장
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  $$('.reveal').forEach(function (el) { io.observe(el); });

  // 숫자 카운트
  var cio = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target, to = parseFloat(el.dataset.count);
      cio.unobserve(el);
      if (isNaN(to)) return;
      var dec = (el.dataset.count.split('.')[1] || '').length, t0 = performance.now(), dur = 1400;
      (function tick(t) {
        var p = Math.min(1, (t - t0) / dur), k = 1 - Math.pow(1 - p, 3);
        el.textContent = (to * k).toFixed(dec);
        if (p < 1) requestAnimationFrame(tick);
      })(t0);
    });
  }, { threshold: 0.5 });
  $$('[data-count]').forEach(function (el) { cio.observe(el); });

  // 헤더
  var hdr = $('[data-header]');
  if (hdr) {
    var onS = function () { hdr.classList.toggle('scrolled', window.scrollY > 40 || !$('.hero')); };
    addEventListener('scroll', onS, { passive: true }); onS();
  }

  // 지금 페이지 메뉴 표시
  $$('[data-nav] a[data-nav]').forEach(function (a) { if (a.pathname === location.pathname) { a.classList.add('on'); a.setAttribute('aria-current', 'page'); } });

  // 모바일 메뉴
  var btn = $('[data-menu-btn]'), nav = $('[data-nav]');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open'); btn.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a') && nav.classList.contains('open')) { nav.classList.remove('open'); btn.setAttribute('aria-expanded', false); document.body.style.overflow = ''; }
    });
  }

  // 고객사 · 사진 흐름 복제
  $$('.marquee__track, [data-strip]').forEach(function (tr) { tr.innerHTML += tr.innerHTML; });

  // 메인 슬라이드
  var slides = $$('.hero .slide'), dotsBox = $('[data-hero-dots]');
  if (slides.length > 1 && dotsBox) {
    var i = 0, t, dots = slides.map(function (_, n) {
      var b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', (n + 1) + '번 사진'); if (n === 0) b.className = 'on';
      b.addEventListener('click', function () { go(n); }); dotsBox.appendChild(b); return b;
    });
    var go = function (n) {
      slides[i].classList.remove('on'); dots[i].classList.remove('on');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('on'); dots[i].classList.add('on');
      clearTimeout(t); t = setTimeout(function () { go(i + 1); }, 5000);
    };
    t = setTimeout(function () { go(1); }, 5000);
  }

  // 시공 사례 필터
  var wtabs = $$('[data-tabs] button'), works = $$('[data-works] .work');
  wtabs.forEach(function (b) {
    b.addEventListener('click', function () {
      wtabs.forEach(function (x) { x.classList.remove('on'); }); b.classList.add('on');
      var f = b.dataset.f;
      works.forEach(function (w) { w.classList.toggle('hide', f !== 'all' && w.dataset.c !== f); if (!w.classList.contains('hide')) w.classList.add('in'); });
    });
  });

  // 확대 보기
  var lb = $('[data-lbox]'), lbl = [], lbt = [], li = 0, lbi, lbc;
  function show(n) {
    li = (n + lbl.length) % lbl.length; lbi.src = lbl[li];
    lbc.textContent = (li + 1) + ' / ' + lbl.length + (lbt[li] ? '  ·  ' + lbt[li] : '');
    [li + 1, li - 1].forEach(function (k) { (new Image()).src = lbl[(k + lbl.length) % lbl.length]; });
  }
  function openLb(arr, n, caps) { lbl = arr; lbt = caps || []; lb.hidden = false; document.body.style.overflow = 'hidden'; show(n); }
  function closeLb() { lb.hidden = true; document.body.style.overflow = ''; lbi.removeAttribute('src'); }
  if (lb) {
    lbi = $('img', lb); lbc = $('.ct', lb);
    $('.x', lb).addEventListener('click', closeLb);
    $('.pv', lb).addEventListener('click', function () { show(li - 1); });
    $('.nx', lb).addEventListener('click', function () { show(li + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') closeLb(); if (e.key === 'ArrowLeft') show(li - 1); if (e.key === 'ArrowRight') show(li + 1);
    });
    // 모바일: 좌우로 밀어 넘기기, 아래로 내려 닫기
    var tx = 0, ty = 0, dx = 0, dy = 0, touching = false;
    lb.addEventListener('touchstart', function (e) { if (e.touches.length !== 1) return; touching = true; tx = e.touches[0].clientX; ty = e.touches[0].clientY; dx = dy = 0; lbi.style.transition = 'none'; }, { passive: true });
    lb.addEventListener('touchmove', function (e) {
      if (!touching) return;
      dx = e.touches[0].clientX - tx; dy = e.touches[0].clientY - ty;
      if (Math.abs(dx) > Math.abs(dy)) lbi.style.transform = 'translateX(' + dx + 'px)'; else if (dy > 0) lbi.style.transform = 'translateY(' + dy + 'px)';
      e.preventDefault();
    }, { passive: false });
    lb.addEventListener('touchend', function () {
      if (!touching) return;
      touching = false; lbi.style.transition = 'transform .25s ease';
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {
        var d = dx < 0 ? 1 : -1; lbi.style.transform = 'translateX(' + (-d * window.innerWidth) + 'px)';
        setTimeout(function () {
          lbi.style.transition = 'none'; show(li + d); lbi.style.transform = 'translateX(' + (d * window.innerWidth * 0.4) + 'px)';
          requestAnimationFrame(function () { requestAnimationFrame(function () { lbi.style.transition = 'transform .25s ease'; lbi.style.transform = ''; }); });
        }, 180);
      } else if (dy > 90 && dy > Math.abs(dx)) { lbi.style.transform = ''; closeLb(); } else lbi.style.transform = '';
    });
  }

  // 갤러리: 서버가 그린 사진을 분류 · 더 보기로 나눠 보인다(자바스크립트가 없어도 전부 보인다)
  var grid = $('[data-ggrid]');
  if (grid) {
    var cells = $$('a', grid), more = $('[data-gmore]'), tabs = $$('[data-gtabs] button'), cur = 'all', STEP = window.innerWidth < 640 ? 18 : 24, shown = 0, list = cells;
    // 같은 사진이 두 분류에 들어 있으면 '전체'에는 한 번만 보인다.
    var seen = new Set(), unique = cells.filter(function (a) { if (seen.has(a.dataset.full)) return false; seen.add(a.dataset.full); return true; });
    var render = function (reset) {
      if (reset) { shown = 0; list = cur === 'all' ? unique : cells.filter(function (a) { return a.dataset.g === cur; }); }
      shown = Math.min(list.length, shown + STEP);
      var on = new Set(list.slice(0, shown));
      cells.forEach(function (a) { a.hidden = !on.has(a); });
      if (more) { more.parentNode.hidden = shown >= list.length; more.parentNode.style.display = shown >= list.length ? 'none' : ''; $('span', more).textContent = '(' + shown + ' / ' + list.length + ')'; }
    };
    tabs.forEach(function (b) {
      var n = b.dataset.g === 'all' ? unique.length : cells.filter(function (a) { return a.dataset.g === b.dataset.g; }).length;
      $('i', b).textContent = n; if (n === 0) b.hidden = true;
      b.addEventListener('click', function () { tabs.forEach(function (x) { x.classList.remove('on'); }); b.classList.add('on'); cur = b.dataset.g; render(true); });
    });
    if (more) more.addEventListener('click', function () { render(false); });
    render(true);
    if (cells.length === 0) { var sec = grid.closest('section'); if (sec) sec.hidden = true; }
    grid.addEventListener('click', function (e) {
      var a = e.target.closest('a'); if (!a || !lb) return;
      e.preventDefault();
      openLb(list.map(function (x) { return x.dataset.full; }), list.indexOf(a), list.map(function (x) { var im = $('img', x); return im && !/현장 사진$/.test(im.alt) ? im.alt : ''; }));
    });
  }
  var worksBox = $('[data-works]');
  if (worksBox && lb) worksBox.addEventListener('click', function (e) {
    var a = e.target.closest('a[data-lb]'); if (!a) return;
    e.preventDefault();
    var vis = $$('.work:not(.hide)', worksBox);
    openLb(vis.map(function (w) { return w.dataset.full; }), vis.indexOf(a), vis.map(function (w) { return $('h3', w).textContent; }));
  });

  // 사진 칸 키보드(Enter · 스페이스로 확대)
  document.addEventListener('keydown', function (e) {
    if ((e.key === 'Enter' || e.key === ' ') && e.target.closest && e.target.closest('a[data-full]')) { e.preventDefault(); e.target.click(); }
  });

  // 행사 종류 미리 고르기(?type=)
  var type = new URLSearchParams(location.search).get('type'), sel = $('#f-type');
  if (type && sel) $$('option', sel).forEach(function (o) { if (o.text === type) sel.value = o.value; });

  // 이벤트 팝업
  var popup = $('[data-popup]');
  if (popup) {
    var key = 'sororong-popup-hide', today = new Date(Date.now() + 9 * 3600000).toISOString().slice(0, 10), hide = null;
    try { hide = localStorage.getItem(key); } catch (e) {}
    // 2026-12-01 · 2026.12.1 · 2026/12/01 모두 받는다. 읽을 수 없으면 제한 없음으로 본다.
    var day = function (v) { var m = /^\s*(\d{4})\D+(\d{1,2})\D+(\d{1,2})/.exec(v || ''); return m ? m[1] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[3]).slice(-2) : ''; };
    var start = day(popup.dataset.start), end = day(popup.dataset.end);
    if (hide !== today && (!start || start <= today) && (!end || today <= end)) popup.hidden = false;
    var shut = function () { popup.hidden = true; };
    $('[data-popup-close]', popup).addEventListener('click', shut);
    $('[data-popup-today]', popup).addEventListener('click', function () { try { localStorage.setItem(key, today); } catch (e) {} shut(); });
    popup.addEventListener('click', function (e) { if (e.target === popup) shut(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') shut(); });
  }
})();
