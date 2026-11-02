# F안 메뉴별 페이지 생성기: python -I tools/build_f_pages.py (초안 폴더에서)
import re, io, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = io.open(os.path.join(ROOT, 'f.html'), encoding='utf-8').read()
MAN = json.load(io.open(os.path.join(ROOT, 'assets/real/_manifest.json'), encoding='utf-8'))
LIVE = [[m['c'], m['n']] for m in MAN if not m['dup']]

def img(c, n, t=False): return 'assets/real/%s/%s%03d.jpg' % (c, 't/' if t else '', n)

MENU = [  # slug, 메뉴 이름
    ('f-biz.html', '기업 · 관공서 · 학교행사'),
    ('f-family.html', '돌잔치 · 개인행사'),
    ('f-helium.html', '헬륨 · 인쇄 · 레터링풍선'),
    ('f-flower.html', '자이언트플라워 · 꽃풍선 · 벌룬화환'),
    ('f-print.html', '폼보드 · 포맥스 · 실사물'),
    ('f-rental.html', '행사장비 렌탈'),
    ('f-contact.html', '상담문의'),
]
LABEL = {'biz': '기업 · 관공서', 'sch': '학교 · 유치원', 'fam': '돌잔치 · 개인', 'wrt': '벌룬화환', 'flw': '자이언트플라워', 'hel': '헬륨 · 레터링'}

def header(active):
    lis = ''.join('\n        <li><a href="%s"%s>%s</a></li>' % (s, ' class="on" aria-current="page"' if s == active else '', t) for s, t in MENU)
    return '''<header class="hdr scrolled" data-header>
  <div class="wrap">
    <a class="brand" href="f.html"><img src="assets/logo/logo-pink.png" alt="sororong EVENT & BALLOON"></a>
    <nav class="nav" data-nav aria-label="주 메뉴">
      <ul>%s
      </ul>
    </nav>
    <a class="cta" href="f-contact.html#form">상담문의</a>
    <button class="menu-btn" data-menu-btn aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>''' % lis

QUICK = re.search(r'<nav class="quick".*?</nav>', F, re.S).group(0).replace('href="#contact"', 'href="f-contact.html#form"')
FORM = re.search(r'<form class="form reveal" data-form novalidate>.*?</form>', F, re.S).group(0)
WAYS = re.search(r'<div class="ways reveal" data-delay="3">.*?</div>', F, re.S).group(0)
FOOTER = re.search(r'<footer>.*?</footer>', F, re.S).group(0)
LB = '<div class="lb" data-lbox hidden><button class="x" aria-label="닫기">×</button><button class="pv" aria-label="이전 사진">‹</button><img alt=""><button class="nx" aria-label="다음 사진">›</button><div class="ct"></div></div>'

STEPS = [('상담', '행사 날짜와 장소, 원하는 분위기를 알려주세요. 참고 사진이 있으면 더 좋아요.'),
         ('디자인 · 견적', '공간 크기와 예산에 맞춘 디자인 시안과 견적을 보내드립니다.'),
         ('제작 · 준비', '확정된 디자인으로 풍선과 실사물, 장비를 준비합니다.'),
         ('설치 · 철거', '행사 전에 설치하고, 끝나면 현장을 깨끗하게 정리합니다.')]

def page_head(title, desc):
    return '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s | 소로롱 이벤트&amp;벌룬</title>
<meta name="description" content="%s">
<link rel="stylesheet" href="assets/common.css">
<link rel="stylesheet" href="assets/f.css?v=1102">
<link rel="stylesheet" href="assets/f-sub.css?v=1102">
</head>
<body>
''' % (title, desc)

def phero(p):
    c, n = p['hero']
    return '''<section class="phero">
  <img src="%s" alt="%s 현장 사진">
  <div class="wrap">
    <div class="crumb"><a href="f.html">홈</a><span>·</span><span>%s</span></div>
    <div class="en">%s</div>
    <h1>%s</h1>
    <p>%s</p>
  </div>
</section>''' % (img(c, n), p['name'], p['name'], p['en'], p['h1'], p['sub'])

def faq(items):
    d = ''.join('\n      <details%s><summary>%s</summary><div class="a">%s</div></details>' % (' open' if i == 0 else '', q, a) for i, (q, a) in enumerate(items))
    return '''<section class="faq">
  <div class="wrap">
    <div class="eyebrow reveal">FAQ</div>
    <h2 class="h2 reveal" data-delay="1">자주 묻는 질문</h2>
    <div class="list reveal" data-delay="2">%s
    </div>
  </div>
</section>''' % d

def steps():
    s = ''.join('\n      <div class="step reveal"%s><b>%02d</b><h3>%s</h3><p>%s</p></div>' % ('' if i == 0 else ' data-delay="%d"' % i, i + 1, t, d) for i, (t, d) in enumerate(STEPS))
    return '''<section class="process">
  <div class="wrap">
    <div class="eyebrow reveal">Process</div>
    <h2 class="h2 reveal" data-delay="1">이렇게 진행돼요</h2>
    <div class="steps">%s
    </div>
  </div>
</section>''' % s

CTA = '''<section class="ctaband">
  <div class="wrap">
    <div><h2>행사 날짜와 장소만 알려주세요</h2><p>어울리는 연출과 견적을 빠르게 제안드립니다.</p></div>
    <div class="btns"><a class="kk" href="#">카카오톡 문의</a><a href="f-contact.html#form">상담 신청하기 →</a></div>
  </div>
</section>'''

def others(cur):
    cells = ''.join('<a href="%s"><img src="%s" alt="" loading="lazy"><span>%s</span></a>' % (p['slug'], img(*p['thumb'], t=True), p['name']) for p in PAGES if p['slug'] != cur)
    return '''<section class="others">
  <div class="wrap">
    <div class="eyebrow reveal">More services</div>
    <h2 class="h2 reveal" data-delay="1">다른 서비스도 둘러보세요</h2>
    <div class="row reveal" data-delay="2">%s</div>
  </div>
</section>''' % cells

def gallery(p):
    data = p['photos']
    cats = []
    for c, _ in data:
        if c not in cats: cats.append(c)
    tabs = ''
    if len(cats) > 1:
        tabs = '<div class="tabs gtabs" data-gtabs><button class="on" data-g="all">전체 <i>%d</i></button>%s</div>' % (len(data), ''.join('<button data-g="%s">%s <i>%d</i></button>' % (c, LABEL[c], sum(1 for x in data if x[0] == c)) for c in cats))
    note = '\n    <div class="note">%s</div>' % p['note'] if p.get('note') else ''
    return '''<section class="gallery" id="gallery">
  <div class="wrap">
    <div class="eyebrow reveal">Gallery</div>
    <h2 class="h2 reveal" data-delay="1">%s 현장 사진</h2>
    <p class="lead reveal" data-delay="2">사진을 누르면 크게 볼 수 있어요. 지금까지 %d장의 현장을 모았습니다.</p>%s
    %s
    <div class="ggrid" data-ggrid></div>
    <div class="gmore"><button data-gmore>사진 더 보기 <span></span></button></div>
  </div>
</section>
%s
<script type="application/json" id="gdata">%s</script>''' % (p['short'], len(data), note, tabs, LB, json.dumps(data, separators=(',', ':')))

def menu_page(p):
    incl = ''.join('<li>%s</li>' % x for x in p['incl'])
    items = ''.join('\n      <div class="item reveal"%s><div class="ph"><img src="%s" alt="%s" loading="lazy"></div><div class="t"><div class="no">%02d</div><h3>%s</h3><p>%s</p></div></div>' % ('' if i == 0 else ' data-delay="%d"' % i, img(c, n), t, i + 1, t, d) for i, (c, n, t, d) in enumerate(p['items']))
    body = '''%s

%s

%s

<section class="intro">
  <div class="wrap grid">
    <div>
      <div class="eyebrow reveal">About</div>
      <h2 class="h2 reveal" data-delay="1">%s</h2>
      <p class="lead reveal" data-delay="2">%s</p>
    </div>
    <div class="reveal" data-delay="2">
      <div class="incl-t">이런 것까지 함께 준비해요</div>
      <ul class="incl">%s</ul>
    </div>
  </div>
</section>

<section class="items">
  <div class="wrap">
    <div class="eyebrow reveal">Services</div>
    <h2 class="h2 reveal" data-delay="1">대표 서비스</h2>
    <div class="item-grid">%s
    </div>
  </div>
</section>

%s

%s

%s

%s

%s
''' % (header(p['slug']), QUICK, phero(p), p['h2'], p['intro'], incl, items, gallery(p), steps(), faq(p['faq']), CTA, others(p['slug']))
    return page_head(p['name'], p['sub']) + body + FOOTER + '\n<script src="assets/common.js?v=1102"></script>\n<script src="assets/f-gallery.js?v=1102"></script>\n</body>\n</html>\n'

def contact_page():
    p = {'name': '상담문의', 'en': 'Contact', 'hero': ('biz', 40), 'h1': '어떤 행사든 편하게 물어보세요', 'sub': '행사 날짜와 장소, 원하는 분위기를 남겨주시면 어울리는 연출과 견적을 제안드립니다.'}
    prep = [('행사 날짜 · 시간', '설치 가능한 시간과 행사 시작 시간을 함께 알려주세요.'),
            ('장소 · 공간 크기', '실내외 여부, 천장 높이, 설치할 벽이나 무대 크기를 알려주세요.'),
            ('인원 · 예산', '대략적인 참석 인원과 생각하는 예산이 있으면 맞춰 제안드려요.'),
            ('참고 사진', '원하는 분위기의 사진이나 로고, 브랜드 컬러를 보내주세요.')]
    pl = ''.join('<li class="reveal"%s><b>%s</b><span>%s</span></li>' % ('' if i == 0 else ' data-delay="%d"' % i, a, b) for i, (a, b) in enumerate(prep))
    contact = '''<section class="contact" id="form">
  <div class="wrap grid">
    <div>
      <div class="eyebrow reveal">Contact</div>
      <h2 class="h2 reveal" data-delay="1">상담 신청</h2>
      <p class="lead reveal" data-delay="2">카카오톡이 가장 빨라요. 참고 사진은 카카오톡으로 보내주시면 함께 확인합니다.</p>
      %s
    </div>
    %s
  </div>
</section>''' % (WAYS, FORM)
    gfaq = re.findall(r'<details(?: open)?><summary>(.*?)</summary><div class="a">(.*?)</div></details>', F)[:4]
    body = '''%s

%s

%s

<section class="prep-sec">
  <div class="wrap">
    <div class="eyebrow reveal">Before you ask</div>
    <h2 class="h2 reveal" data-delay="1">이 네 가지를 알려주시면 견적이 빨라요</h2>
    <ul class="prep">%s</ul>
  </div>
</section>

%s

%s

%s

%s
''' % (header('f-contact.html'), QUICK, phero(p), pl, contact, steps(), faq(gfaq), others('f-contact.html'))
    js = '''<script>
(function(){ var form=document.querySelector('[data-form]'); form.addEventListener('submit',function(e){ e.preventDefault(); if(!form.checkValidity()){ form.reportValidity(); return; } form.classList.add('sent'); });
  var t=new URLSearchParams(location.search).get('type'); if(t){ var s=document.getElementById('f-type'); [].forEach.call(s.options,function(o){ if(o.text===t) s.value=o.value; }); } })();
</script>'''
    return page_head('상담문의', p['sub']) + body + FOOTER + '\n<script src="assets/common.js?v=1102"></script>\n' + js + '\n</body>\n</html>\n'

PRINT = [('sch', n) for n in (25, 29, 37, 46, 71, 78, 12)] + [('biz', n) for n in (5, 11, 33, 60, 96, 101, 115, 125)]
RENTAL = [('biz', n) for n in (62, 127, 141, 142, 63, 99, 89, 117, 88, 111, 132)] + [('sch', n) for n in (3, 39, 91)]
NOTE = '실사물 · 장비 전용 사진은 다음 사진을 받으면 추가합니다. 지금은 함께 진행한 현장 사진입니다.'

PAGES = [
 dict(slug='f-biz.html', name='기업 · 관공서 · 학교행사', short='기업 · 관공서 · 학교', en='Corporate · Public · School', hero=('biz', 93), thumb=('biz', 87),
  h1='행사의 격을 높이는<br>공간 연출', sub='시상식과 기념식, 매장 오픈과 팝업, 관공서 행사, 유치원과 학교 행사까지 목적에 맞게 디자인합니다.',
  h2='브랜드 컬러와 행사 목적에<br>꼭 맞춘 디자인',
  intro='기업 시상식과 기념식, 송년회부터 매장 오픈과 브랜드 팝업, 관공서 기념식, 유치원과 학교의 입학식 · 졸업식 · 축제까지. 행사 목적과 브랜드 컬러, 공간 크기에 맞춰 디자인하고 제작부터 설치 · 철거까지 직접 진행합니다.',
  incl=['포토월 · 백월', '입구 아치 · 풍선 기둥', '무대 전면 · 단상 장식', '대형 조형 풍선', '로고 · 숫자 오브제', '실사 출력물 · 레드카펫'],
  items=[('biz', 87, '기념식 · 시상식', '창립 기념일, 연말 시상식, 송년의 밤 포토월과 무대 장식'),
         ('biz', 45, '브랜드 팝업 · 매장 오픈', '브랜드 컬러와 로고를 살린 매장 입구, 쇼윈도, 팝업 연출'),
         ('biz', 60, '관공서 · 공공기관 행사', '개관식, 기념식, 지역 행사의 무대와 포토존'),
         ('sch', 73, '학교 · 유치원 행사', '입학식, 졸업식, 학교 축제의 아치와 무대 장식')],
  photos=[x for x in LIVE if x[0] in ('biz', 'sch')],
  faq=[('행사 전날이나 이른 아침 설치도 가능한가요?', '네. 행사 일정에 맞춰 전날 저녁이나 당일 이른 시간에 설치하고, 행사가 끝나면 철거까지 진행합니다.'),
       ('브랜드 가이드나 로고 컬러를 맞춰 줄 수 있나요?', '가능합니다. 로고 파일과 컬러 코드를 보내주시면 풍선 색상, 인쇄 풍선, 실사물까지 브랜드에 맞춰 제안드립니다.'),
       ('학교 · 기관은 서류 처리가 되나요?', '견적서와 세금계산서 등 필요한 서류를 함께 준비해 드립니다.'),
       ('참고 사진과 똑같이 만들어 줄 수 있나요?', '참고 사진의 분위기를 바탕으로 공간 크기와 예산에 맞게 다시 디자인해 드립니다.')]),
 dict(slug='f-family.html', name='돌잔치 · 개인행사', short='돌잔치 · 개인행사', en='Family · Private', hero=('fam', 5), thumb=('fam', 17),
  h1='가족의 하루를<br>사진으로 남기는 공간', sub='돌잔치와 칠순 잔치, 생일 파티까지. 이름과 날짜, 원하는 색감으로 꾸며 드립니다.',
  h2='아이 이름과 테마 색으로<br>하나뿐인 돌상을',
  intro='돌잔치와 칠순 · 팔순 잔치, 생일 파티, 브라이덜 샤워까지. 아이 이름과 날짜, 원하는 색감과 테마에 맞춰 돌상과 포토존을 꾸미고, 행사 시간에 맞춰 설치합니다.',
  incl=['돌상 · 포토 테이블', '이름 · 날짜 보드', '라이트 숫자', '생화 · 조화 장식', '테마 인형 · 소품', '헬륨 · 버블 풍선'],
  items=[('fam', 17, '돌잔치', '아이 이름과 테마 색으로 꾸미는 돌상과 포토존'),
         ('fam', 13, '칠순 · 팔순 잔치', '부모님 잔치를 위한 품격 있는 테이블과 숫자 장식'),
         ('fam', 1, '생일 파티', '캐릭터 테마와 풍선 기둥으로 채우는 생일 테이블'),
         ('fam', 7, '홈파티 · 파티룸', '파티룸과 집에서 여는 작은 행사 연출')],
  photos=[x for x in LIVE if x[0] == 'fam'],
  faq=[('언제까지 예약해야 하나요?', '주말은 일정이 빨리 차서 행사 2~4주 전 문의를 권해드립니다. 일정이 비어 있으면 가까운 날짜도 가능합니다.'),
       ('돌잔치 전문점이나 파티룸에도 설치할 수 있나요?', '네. 돌잔치 전문점, 파티룸, 식당, 집 등 장소 상황을 확인한 뒤 설치합니다.'),
       ('아이 이름이나 날짜를 넣은 보드도 만들어 주나요?', '이름 · 날짜 보드와 레터링 풍선을 함께 제작해 드립니다.'),
       ('행사가 끝나면 소품은 어떻게 하나요?', '대여 소품은 행사 후 회수하고, 풍선과 레터링 풍선은 가져가실 수 있습니다.')]),
 dict(slug='f-helium.html', name='헬륨 · 인쇄 · 레터링풍선', short='헬륨 · 레터링 풍선', en='Helium · Print · Lettering', hero=('hel', 9), thumb=('hel', 7),
  h1='문구 하나로<br>특별해지는 풍선', sub='헬륨 풍선 번들, 로고 인쇄 풍선, 이름을 새긴 버블 레터링 풍선을 만듭니다.',
  h2='행사 포인트부터<br>선물까지',
  intro='헬륨 풍선 번들, 로고와 문구를 인쇄한 풍선, 이름을 새긴 버블 레터링 풍선까지. 행사장 포인트부터 선물용까지 수량과 용도에 맞춰 제작하고 직접 전달하거나 설치합니다.',
  incl=['헬륨 풍선 번들', '로고 인쇄 풍선', '버블 레터링 풍선', '은박 숫자 · 글자 풍선', '천장 띄우기 연출', '꽃다발과 함께 구성'],
  items=[('hel', 2, '헬륨 풍선 장식', '행사장 테이블과 공간을 채우는 헬륨 번들'),
         ('hel', 5, '로고 · 문구 풍선', '기념일 문구와 로고를 넣은 맞춤 풍선'),
         ('hel', 7, '버블 레터링 풍선', '투명 버블 풍선에 이름과 축하 문구'),
         ('hel', 10, '은박 하트 · 별 풍선', '선물과 이벤트를 위한 은박 풍선 묶음')],
  photos=[x for x in LIVE if x[0] == 'hel'],
  faq=[('헬륨 풍선은 얼마나 떠 있나요?', '일반 고무풍선은 보통 하루 안팎, 은박과 버블 풍선은 그보다 오래 떠 있습니다. 행사 시간에 맞춰 당일 준비해 드립니다.'),
       ('소량 주문도 되나요?', '선물용 소량도 가능합니다. 수량과 받을 날짜를 알려주세요.'),
       ('로고 인쇄 풍선은 얼마나 걸리나요?', '인쇄 일정이 필요해 보통 1~2주 여유를 두고 문의해 주시면 좋습니다.'),
       ('원하는 문구를 넣을 수 있나요?', '네. 이름, 날짜, 축하 문구를 원하는 글씨체로 넣어 드립니다.')]),
 dict(slug='f-flower.html', name='자이언트플라워 · 꽃풍선 · 벌룬화환', short='꽃풍선 · 벌룬화환', en='Giant flower · Balloon wreath', hero=('flw', 5), thumb=('wrt', 6),
  h1='축하의 마음을<br>크게 전하는 꽃과 화환', sub='응원 · 축하 벌룬화환과 꽃풍선, 공간을 채우는 자이언트 플라워를 제작합니다.',
  h2='받는 분의 이름과<br>응원 문구를 담아',
  intro='개업과 공연, 전시, 졸업을 축하하는 벌룬화환과 꽃풍선, 공간의 분위기를 단번에 바꾸는 자이언트 플라워를 제작합니다. 받는 분의 이름과 응원 문구, 좋아하는 색을 담아 드립니다.',
  incl=['응원 · 축하 벌룬화환', '사진 · 문구 리본', '자이언트 플라워', '꽃풍선 · 플라워 박스', '전시 · 무대 플라워', '현장 전달 · 설치'],
  items=[('wrt', 6, '벌룬화환', '이름 풍선과 리본 문구를 넣은 축하 화환'),
         ('wrt', 11, '공연 · 응원 화환', '공연장과 행사장으로 보내는 컬러 화환'),
         ('flw', 3, '자이언트 플라워', '전시 부스와 무대를 채우는 대형 종이꽃'),
         ('flw', 1, '촬영 · 돌잔치 플라워', '포토존 포인트가 되는 대형 꽃 소품')],
  photos=[x for x in LIVE if x[0] in ('wrt', 'flw')],
  faq=[('화환은 언제까지 주문해야 하나요?', '제작 시간이 필요해 최소 3~5일 전 주문을 권해드립니다. 급한 일정은 먼저 문의해 주세요.'),
       ('공연장이나 행사장으로 바로 보내줄 수 있나요?', '네. 받는 장소의 반입 규정을 확인한 뒤 시간에 맞춰 전달합니다.'),
       ('사진이나 문구를 넣을 수 있나요?', '받는 분 사진, 이름 풍선, 응원 문구 리본을 넣어 드립니다.'),
       ('자이언트 플라워는 대여도 되나요?', '행사 기간 동안 대여하거나 제작해 드립니다. 크기와 수량을 알려주세요.')]),
 dict(slug='f-print.html', name='폼보드 · 포맥스 · 실사물', short='폼보드 · 실사물', en='Print · Signage', hero=('sch', 29), thumb=('sch', 25),
  h1='풍선과 함께 완성하는<br>실사물', sub='포토월 백월, 환영 보드, 캐릭터 등신대, 현수막까지 풍선 장식과 한 번에 준비합니다.',
  h2='디자인부터 출력, 설치까지<br>한 번에',
  intro='포토월 백월, 환영 보드, 캐릭터 등신대, 입간판과 현수막까지. 풍선 장식과 어울리도록 디자인부터 출력, 설치까지 한 번에 진행해 행사 준비를 줄여 드립니다.',
  incl=['폼보드 · 포맥스 보드', '캐릭터 · 인물 등신대', '포토월 백월 실사', '환영 · 안내 보드', '현수막 · 배너', '숫자 · 글자 조형물'],
  items=[('sch', 29, '환영 보드 · 포토 프레임', '캐릭터와 문구를 넣은 입학식 환영 보드'),
         ('biz', 115, '포토월 백월 실사', '행사명과 로고를 출력한 대형 백월'),
         ('sch', 37, '캐릭터 등신대', '아이들이 좋아하는 캐릭터 폼보드 컷'),
         ('biz', 5, '현수막 · 무대 배너', '무대 전면을 채우는 행사 현수막')],
  photos=PRINT, note=NOTE,
  faq=[('디자인 파일이 없어도 되나요?', '네. 행사명과 문구, 로고만 주시면 풍선 장식과 어울리게 디자인해 드립니다.'),
       ('제작 기간은 얼마나 걸리나요?', '디자인 확정 후 보통 3~5일이 걸립니다. 크기와 수량에 따라 달라질 수 있어요.'),
       ('행사 후 보드를 가져갈 수 있나요?', '제작물은 가져가실 수 있고, 다음 행사에 다시 쓰도록 보관 방법도 안내해 드립니다.'),
       ('원하는 크기로 만들 수 있나요?', '설치 공간을 확인한 뒤 알맞은 크기와 소재를 제안드립니다.')]),
 dict(slug='f-rental.html', name='행사장비 렌탈', short='행사장비 렌탈', en='Rental', hero=('biz', 127), thumb=('biz', 62),
  h1='행사 준비를<br>장비까지 한 번에', sub='천막, 테이블, 레드카펫, 트러스, 단상까지 풍선 장식과 함께 준비합니다.',
  h2='운반부터 설치, 철거까지<br>맡겨 주세요',
  intro='천막과 테이블, 레드카펫, 트러스, 단상처럼 행사에 필요한 기본 장비를 풍선 장식과 함께 준비합니다. 운반과 설치, 철거까지 맡겨 주시면 행사 당일은 진행에만 집중하실 수 있어요.',
  incl=['천막 · 그늘막', '테이블 · 의자', '레드카펫 · 컬러카펫', '트러스 · 포토월 프레임', '단상 · 무대 소품', '조명 · 라이트 숫자'],
  items=[('biz', 62, '천막 · 테이블', '야외 행사와 체육대회를 위한 천막과 테이블'),
         ('biz', 99, '레드카펫', '입장 동선을 만드는 레드카펫과 객석 장식'),
         ('biz', 111, '트러스 · 포토월 프레임', '대형 백월을 세우는 트러스 구조물'),
         ('sch', 3, '무대 · 컬러카펫', '학교 축제 무대와 컬러 카펫 연출')],
  photos=RENTAL, note=NOTE,
  faq=[('장비만 따로 빌릴 수 있나요?', '가능합니다. 풍선 장식 없이 장비만 필요한 경우에도 문의해 주세요.'),
       ('대여 기간은 어떻게 되나요?', '보통 행사 당일 기준이며, 여러 날 행사는 기간에 맞춰 견적을 드립니다.'),
       ('야외 행사에 비가 오면 어떻게 하나요?', '천막과 고정 장비로 대비하고, 기상 상황에 따라 설치 방식을 함께 조율합니다.'),
       ('설치와 철거도 해주시나요?', '네. 운반, 설치, 철거까지 소로롱이 직접 진행합니다.')]),
]

for p in PAGES:
    io.open(os.path.join(ROOT, p['slug']), 'w', encoding='utf-8', newline='\n').write(menu_page(p))
io.open(os.path.join(ROOT, 'f-contact.html'), 'w', encoding='utf-8', newline='\n').write(contact_page())
print('pages:', [p['slug'] for p in PAGES] + ['f-contact.html'])
