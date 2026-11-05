# 소로롱 F안 → 탱탱소프트 CMS 사이트 묶음 생성기
#   python -I tools/build_cms_site.py <TengTeng-Soft 작업 폴더>   (초안 폴더에서)
#
# 만드는 것
#   sites/sororong/{site.json,pages,partials}   템플릿(사진 칸은 고객이 관리자에서 바꾼다)
#   public/_tpl/sororong/                        CSS · JS · 로고 · 칸 기본 사진(사진을 빼도 화면이 깨지지 않게)
#   tools/cms_seed.json                          관리자에 처음 넣을 사진 목록(tools/cms_load.mjs 가 쓴다)
#
# 문구는 build_f_pages.py 의 PAGES 와 f.html 을 그대로 쓴다. 시안과 실제 사이트가 어긋나지 않게 하려는 것이다.
import io, json, os, re, shutil, sys, importlib.util
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = sys.argv[1] if len(sys.argv) > 1 else 'D:/work/.worktrees/tt-sororong-cms'
OUT = os.path.join(REPO, 'sites/sororong'); TPL = os.path.join(REPO, 'public/_tpl/sororong')
spec = importlib.util.spec_from_file_location('fp', os.path.join(ROOT, 'tools/build_f_pages.py')); fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
F = fp.F; PAGES = fp.PAGES
ORD = json.load(io.open(os.path.join(ROOT, 'assets/real/_order.json'), encoding='utf-8'))
CAPS = ORD['caps']

KEY = {'f-biz.html': 'biz', 'f-family.html': 'family', 'f-helium.html': 'helium', 'f-flower.html': 'flower', 'f-print.html': 'print', 'f-rental.html': 'rental', 'f-review.html': 'review'}
CARD = {'biz': 'cardBiz', 'family': 'cardFamily', 'helium': 'cardHelium', 'flower': 'cardFlower', 'print': 'cardPrint', 'rental': 'cardRental', 'review': 'cardReview'}
GAL = {'biz': 'galBiz', 'sch': 'galSch', 'fam': 'galFam', 'wrt': 'galWrt', 'flw': 'galFlw', 'hel': 'galHel', 'prt': 'galPrint', 'rnt': 'galRental', 'rev': 'galReview'}
GLABEL = {'biz': '기업 · 관공서', 'sch': '학교 · 유치원', 'fam': '돌잔치 · 개인', 'wrt': '벌룬화환', 'flw': '자이언트플라워', 'hel': '헬륨 · 레터링', 'prt': '폼보드 · 실사물', 'rnt': '행사장비', 'rev': '연예인 서포트'}
FULL = {'biz': '기업 · 관공서 · 학교행사', 'family': '돌잔치 · 개인행사', 'helium': '헬륨 · 인쇄 · 레터링풍선', 'flower': '자이언트플라워 · 꽃풍선 · 벌룬화환', 'print': '폼보드 · 포맥스 · 실사물', 'rental': '행사장비 렌탈', 'review': '연예인 서포트 후기'}
NAVL = {'review': '서포트 후기'}
SHORT = {'review': '연예인 서포트 후기', 'biz': '기업 · 학교 행사', 'family': '돌잔치 · 개인행사', 'helium': '헬륨 · 레터링', 'flower': '꽃풍선 · 벌룬화환', 'print': '폼보드 · 실사물', 'rental': '행사장비 렌탈'}
MAX_EDGE = 1600

def real(c, n): return 'assets/real/%s/%03d.jpg' % (c, n)
def link(html):
    html = html.replace('f.html', '{{link "/"}}').replace('f-contact.html#form', '{{link "/contact"}}#form').replace('f-contact.html', '{{link "/contact"}}')
    for f, k in KEY.items(): html = html.replace(f, '{{link "/%s"}}' % k)
    return html
def slot(field, cls='', alt='', lazy=True):
    return '<img%s src="{{image content.%s "img/%s.webp"}}" alt="{{alt content.%s "%s"}}"%s>' % (' class="%s"' % cls if cls else '', field, field, field, alt, ' loading="lazy"' if lazy else '')
def esc(s): return s.replace('&', '&amp;')

# ── 콘텐츠 칸 ───────────────────────────────────────────────────────────────
fields = {}; order = []; seed = {}; fallbacks = {}
def add(key, schema): fields[key] = schema; order.append(key)
def image_slot(key, label, source, alt='', help_=None):
    s = {'type': 'image', 'label': label, 'maxEdge': MAX_EDGE}
    if help_: s['help'] = help_
    add(key, s); seed[key] = {'file': real(*source), 'alt': alt}; fallbacks[key] = real(*source)
def photos(key, label, items, max_items=400, help_=None):
    add(key, {'type': 'list', 'label': label, 'maxItems': max_items, 'display': 'photos', **({'help': help_} if help_ else {}),
              'item': {'fields': {'image': {'type': 'image', 'label': '사진', 'maxEdge': MAX_EDGE}}, 'order': ['image']}})
    seed[key] = [{'file': real(c, n), 'alt': alt} for c, n, alt in items]
def rows(cat): return [(c, n, CAPS.get('%s/%d' % (c, n), '')) for c, n in ORD['order'][cat]]

# 메인
hero_src = re.findall(r'<div class="slide(?: on)?"><img src="assets/real/(\w+)/(\d+)\.jpg" alt="([^"]*)"', F)
hero = [(c, int(n), a) for c, n, a in hero_src]
photos('heroSlides', '메인 슬라이드 사진', hero, 12, '첫 화면에 크게 돌아가는 사진입니다. 12장까지 넣을 수 있고, 가로로 긴 사진이 잘 어울립니다.')
svc_src = re.findall(r'<a class="svc reveal"[^>]*href="(f-\w+\.html)"><img src="assets/real/(\w+)/(\d+)\.jpg"', F)
for f, c, n in svc_src:
    k = KEY[f]
    if k == 'rental': c, n = 'rnt', 1
    image_slot(CARD[k], '서비스 카드 · %s' % FULL[k], (c, int(n)), FULL[k])
image_slot('cardReview', '서비스 카드 · 연예인 서포트 후기', ('rev', 4), '연예인 서포트 후기')
strip_src = re.findall(r'assets/real/(\w+)/t/(\d+)\.jpg', re.search(r'<section class="strip".*?</section>', F, re.S).group(0))
strip_seen = []
for c, n in strip_src:
    if (c, int(n)) not in strip_seen: strip_seen.append((c, int(n)))
photos('strip', '하단 사진 흐름', [(c, n, '') for c, n in strip_seen], 40, '메인 화면 아래쪽에서 천천히 흐르는 사진입니다.')

# 시공 사례
works = []
for c, _d, href, title, k, h3, p in re.findall(r'<a class="work reveal" data-c="(\w+)"((?: data-delay="\d")?) href="([^"]+)" data-lb><div class="ph"><img src="[^"]+" alt="([^"]*)" loading="lazy"></div><div class="cap"><div class="k">([^<]*)</div><h3>([^<]*)</h3><p>([^<]*)</p></div></a>', F):
    works.append({'cat': c, 'kicker': k, 'title': h3, 'desc': p, 'file': href})
add('works', {'type': 'list', 'label': '시공 사례', 'maxItems': 60, 'itemLabelField': 'title', 'help': '메인 화면 시공 사례입니다. 위에서부터 차례로 보입니다.',
              'item': {'order': ['image', 'title', 'desc', 'kicker', 'cat'], 'fields': {
                  'image': {'type': 'image', 'label': '사진', 'maxEdge': MAX_EDGE},
                  'title': {'type': 'text', 'label': '제목', 'maxLength': 60, 'required': True},
                  'desc': {'type': 'text', 'label': '짧은 설명', 'maxLength': 120},
                  'kicker': {'type': 'text', 'label': '작은 영문 표시', 'maxLength': 30},
                  'cat': {'type': 'select', 'label': '분류', 'required': True, 'options': [{'value': k, 'label': GLABEL[k]} for k in ('biz', 'sch', 'fam', 'wrt', 'flw', 'hel')]}}}})
seed['works'] = [{'file': w['file'], 'title': w['title'], 'desc': w['desc'], 'kicker': w['kicker'], 'cat': w['cat']} for w in works]

# 메뉴별
PRINT_ROWS = [(x[0], x[1], x[2] if len(x) > 2 else '') for x in fp.PRINT]
RENT_ROWS = [(x[0], x[1], x[2] if len(x) > 2 else '') for x in fp.RENTAL]
GALLERIES = {'biz': [('biz', rows('biz')), ('sch', rows('sch'))], 'family': [('fam', rows('fam'))], 'helium': [('hel', rows('hel'))],
             'flower': [('wrt', rows('wrt')), ('flw', rows('flw'))], 'print': [('prt', PRINT_ROWS)], 'rental': [('rnt', RENT_ROWS)], 'review': [('rev', rows('rev'))]}
sections = [{'key': 'home', 'label': '메인 화면 사진', 'fields': ['heroSlides'] + [CARD[k] for k in CARD] + ['strip']}, {'key': 'works', 'label': '시공 사례', 'fields': ['works']}]
for p in PAGES:
    k = KEY[p['slug']]; sec = []
    for g, items in GALLERIES[k]:
        photos(GAL[g], '갤러리 · %s' % GLABEL[g], items); sec.append(GAL[g])
    image_slot(k + 'Hero', '페이지 맨 위 큰 사진', p['hero'][:2], p['name'] + ' 현장 사진'); sec.append(k + 'Hero')
    for i, it in enumerate(p['items'], 1):
        image_slot('%sItem%d' % (k, i), '대표 서비스 %d · %s' % (i, it[2]), it[:2], it[2]); sec.append('%sItem%d' % (k, i))
    sections.append({'key': k, 'label': SHORT[k], 'fields': sec})
image_slot('contactHero', '상담문의 페이지 맨 위 큰 사진', ('biz', 40), '상담문의 현장 사진')
sections.append({'key': 'contact', 'label': '상담문의', 'fields': ['contactHero']})

# 팝업
add('popupOn', {'type': 'boolean', 'label': '이벤트 팝업 보이기', 'help': '켜면 메인 화면에 들어올 때 팝업이 뜹니다. 방문자는 "오늘 하루 보지 않기"로 닫을 수 있습니다.'})
add('popupImage', {'type': 'image', 'label': '팝업 사진', 'maxEdge': 1200})
add('popupLink', {'type': 'url', 'label': '사진을 누르면 갈 주소', 'help': '비워 두면 눌러도 이동하지 않습니다.'})
add('popupStart', {'type': 'text', 'label': '보이기 시작하는 날', 'maxLength': 10, 'placeholder': '2026-12-01', 'help': '비워 두면 바로 보입니다. 2026-12-01 처럼 적어주세요.'})
add('popupEnd', {'type': 'text', 'label': '마지막 날', 'maxLength': 10, 'placeholder': '2026-12-31', 'help': '비워 두면 끌 때까지 보입니다.'})
sections.append({'key': 'popup', 'label': '이벤트 팝업', 'fields': ['popupOn', 'popupImage', 'popupLink', 'popupStart', 'popupEnd']})

# 연락처 · 실적
for key, schema in [
    ('phone', {'type': 'text', 'label': '전화번호', 'maxLength': 20, 'placeholder': '010-0000-0000'}),
    ('kakaoUrl', {'type': 'url', 'label': '카카오톡 채널 주소'}),
    ('instagramUrl', {'type': 'url', 'label': '인스타그램 주소'}),
    ('blogUrl', {'type': 'url', 'label': '네이버 블로그 주소', 'help': '화면에는 보이지 않고, 검색엔진이 같은 업체로 알아보는 데 쓰입니다.'}),
    ('address', {'type': 'text', 'label': '주소', 'maxLength': 120}),
    ('bizInfo', {'type': 'text', 'label': '사업자 정보(맨 아래 표시)', 'maxLength': 160}),
    ('privacyOwner', {'type': 'text', 'label': '개인정보 보호책임자', 'maxLength': 60}),
]: add(key, schema)
add('stats', {'type': 'list', 'label': '실적 숫자', 'maxItems': 4, 'minItems': 1, 'itemLabelField': 'label', 'item': {'order': ['value', 'suffix', 'label'], 'fields': {
    'value': {'type': 'text', 'label': '숫자', 'maxLength': 10, 'required': True}, 'suffix': {'type': 'text', 'label': '단위', 'maxLength': 6}, 'label': {'type': 'text', 'label': '설명', 'maxLength': 30, 'required': True}}}})
add('clients', {'type': 'list', 'label': '함께한 고객사', 'maxItems': 60, 'itemLabelField': 'name', 'help': '메인 화면에서 옆으로 흐릅니다. 로고를 넣으면 이름 대신 로고가 보입니다.', 'item': {'order': ['name', 'logo'], 'fields': {'name': {'type': 'text', 'label': '이름', 'maxLength': 40, 'required': True}, 'logo': {'type': 'image', 'label': '로고(선택)', 'maxEdge': 600}}}})
add('faq', {'type': 'list', 'label': '자주 묻는 질문', 'maxItems': 20, 'itemLabelField': 'question', 'item': {'order': ['question', 'answer'], 'fields': {
    'question': {'type': 'text', 'label': '질문', 'maxLength': 120, 'required': True}, 'answer': {'type': 'text', 'label': '답변', 'maxLength': 400, 'required': True}}}})
sections.append({'key': 'settings', 'label': '연락처 · 실적', 'fields': ['phone', 'kakaoUrl', 'instagramUrl', 'blogUrl', 'address', 'bizInfo', 'privacyOwner', 'stats', 'clients', 'faq']})

FAQ_ALL = re.findall(r'<details(?: open)?><summary>(.*?)</summary><div class="a">(.*?)</div></details>', F)
STATS = [{'value': v, 'suffix': re.sub(r'<.*?>', '', s), 'label': l} for v, s, l in re.findall(r'<div class="stat reveal"[^>]*><b><span data-count="([^"]+)">0</span>(.*?)</b><span>([^<]+)</span></div>', F)]
CLIENTS = [{'name': n.replace('&#39;', "'")} for n in re.findall(r'<span(?: class="ko")?>([^<]+)</span>', re.search(r'<div class="marquee__track">(.*?)</div>', F, re.S).group(1))]
defaults = {'phone': '', 'kakaoUrl': '', 'instagramUrl': '', 'blogUrl': '', 'address': '경기도 광주시', 'bizInfo': '소로롱 이벤트&벌룬 · 경기도 광주시', 'privacyOwner': '소로롱 대표', 'popupOn': False,
            'stats': STATS, 'clients': CLIENTS, 'faq': [{'question': q, 'answer': a} for q, a in FAQ_ALL], 'heroSlides': [], 'strip': [], 'works': []}
for g in GAL.values(): defaults[g] = []

# ── 부분 템플릿 ─────────────────────────────────────────────────────────────
HEAD = '''<meta name="theme-color" content="#fc7294">
    <link rel="stylesheet" href="{{asset "css/site.css"}}">
    <script src="{{asset "js/site.js"}}" defer></script>'''
QUICK = esc(re.search(r'<nav class="quick".*?</nav>', F, re.S).group(0))
QUICK = QUICK.replace('class="kk" href="#"', 'class="kk" href="{{url content.kakaoUrl}}" rel="noopener" target="_blank"').replace('class="tel" href="tel:"', 'class="tel" href="tel:{{tel content.phone}}"')
QUICK = QUICK.replace('class="ig" href="#"', 'class="ig" href="{{url content.instagramUrl}}" rel="noopener" target="_blank"').replace('class="qt" href="#contact"', 'class="qt" href="{{link "/contact"}}#form"')
HEADER = '''<header class="hdr" data-header>
  <div class="wrap">
    <a class="brand" href="{{link "/"}}"><img src="{{asset "img/logo-pink.png"}}" alt="소로롱 이벤트 앤 벌룬"></a>
    <nav class="nav" data-nav aria-label="주 메뉴">
      <ul>NAV_ITEMS</ul>
    </nav>
    <a class="cta" href="{{link "/contact"}}#form">상담문의</a>
    <button class="menu-btn" data-menu-btn aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>
''' + QUICK
HEADER = HEADER.replace('NAV_ITEMS', ''.join('<li><a href="{{link "/%s"}}" data-nav>%s</a></li>' % (k, NAVL.get(k, FULL[k])) for k in FULL) + '<li><a href="{{link "/contact"}}" data-nav>상담문의</a></li>')
FOOTER = '''<footer>
  <div class="wrap">
    <img src="{{asset "img/logo-pink.png"}}" alt="소로롱">
    <div>{{content.bizInfo}}</div>
    <div><a href="{{link "/privacy"}}">개인정보 처리방침</a></div>
    <div>© {{year}} sororong. All rights reserved.</div>
  </div>
</footer>'''
LIGHTBOX = fp.LB
LAYOUT = '''<!doctype html>
<html lang="{{site.lang}}">
<head>
    {{> head}}
</head>
<body>
{{> header}}
<main id="main" class="wrap" data-doc>
  <h1>{{page.heading}}</h1>
  {{blocks}}
</main>
{{> footer}}
</body>
</html>
'''
def page(body):
    return '''<!doctype html>
<html lang="{{site.lang}}">
<head>
    {{> head}}
</head>
<body>
{{> header}}
<main id="main">
''' + body + '''
</main>
{{> footer}}
</body>
</html>
'''
FORM = '''<form class="form reveal" data-tt-form="consult" method="post" action="{{form-action}}" enctype="multipart/form-data">
      {{form "consult"}}
      <h3>간단 상담 접수</h3>
      <div class="sub">남겨주신 연락처로 확인 후 연락드립니다.</div>
      <div class="row">
        <div><label for="f-name">이름</label><input id="f-name" name="name" placeholder="홍길동" required maxlength="40" autocomplete="name"></div>
        <div><label for="f-tel">연락처</label><input id="f-tel" name="phone" type="tel" placeholder="010-0000-0000" required maxlength="20" autocomplete="tel"></div>
      </div>
      <div class="row">
        <div><label for="f-type">행사 종류</label><select id="f-type" name="kind"><option>기업 · 관공서 · 학교행사</option><option>돌잔치 · 개인행사</option><option>헬륨 · 인쇄 · 레터링풍선</option><option>자이언트플라워 · 꽃풍선 · 벌룬화환</option><option>폼보드 · 포맥스 · 실사물 제작</option><option>행사장비 렌탈</option><option>기타</option></select></div>
        <div><label for="f-date">행사 날짜</label><input id="f-date" name="date" type="date"></div>
      </div>
      <div class="row one">
        <div><label for="f-place">장소</label><input id="f-place" name="place" placeholder="예: 경기 광주시 ○○초등학교 강당" maxlength="120"></div>
      </div>
      <div class="row one">
        <div><label for="f-msg">문의 내용</label><textarea id="f-msg" name="message" placeholder="원하는 분위기, 예산 등을 적어주세요" maxlength="2000"></textarea></div>
      </div>
      <div class="row one">
        <div><label for="f-files">참고 사진 (최대 3장)</label><input id="f-files" name="tt_files" type="file" accept="image/*" multiple></div>
      </div>
      <label class="agree"><input type="checkbox" name="tt_consent" value="yes" required> <span>상담 목적의 개인정보 수집 · 이용에 동의합니다. <a href="{{link "/privacy"}}">자세히 보기</a></span></label>
      <button type="submit">상담 신청하기</button>
    </form>'''
WAYS = '''<div class="ways reveal" data-delay="3">
        <a class="kk" href="{{url content.kakaoUrl}}" rel="noopener" target="_blank">카카오톡 채널로 문의</a>
        <a href="{{url content.instagramUrl}}" rel="noopener" target="_blank">인스타그램에서 작업 보기</a>
        <a href="tel:{{tel content.phone}}">전화 문의{{#if content.phone}} ({{content.phone}}){{/if}}</a>
      </div>'''
def gal_html(cats):
    tabs = ''
    if len(cats) > 1:
        tabs = '<div class="tabs gtabs" data-gtabs><button class="on" data-g="all">전체 <i></i></button>%s</div>' % ''.join('<button data-g="%s">%s <i></i></button>' % (c, GLABEL[c]) for c in cats)
    cells = ''.join('{{#each content.%s}}<a role="button" tabindex="0" data-full="{{image image}}" data-g="%s"><img src="{{image image}}" alt="{{alt image "소로롱 %s 풍선 장식 현장 사진"}}" loading="lazy"></a>{{/each}}' % (GAL[c], c, GLABEL[c]) for c in cats)
    return tabs, cells
def gallery(title, lead, cats):
    tabs, cells = gal_html(cats)
    return '''<section class="gallery" id="gallery">
  <div class="wrap">
    <div class="eyebrow reveal">Gallery</div>
    <h2 class="h2 reveal" data-delay="1">%s</h2>
    <p class="lead reveal" data-delay="2">%s</p>
    %s
    <div class="ggrid" data-ggrid>%s</div>
    <div class="gmore"><button type="button" data-gmore>사진 더 보기 <span></span></button></div>
  </div>
</section>
%s''' % (title, lead, tabs, cells, LIGHTBOX)
def others(cur):
    cells = ''.join('<a href="{{link "/%s"}}">%s<span>%s</span></a>' % (k, slot(CARD[k], alt=FULL[k]), FULL[k]) for k in FULL if k != cur)
    return '''<section class="others">
  <div class="wrap">
    <div class="eyebrow reveal">More services</div>
    <h2 class="h2 reveal" data-delay="1">다른 서비스도 둘러보세요</h2>
    <div class="row reveal" data-delay="2">%s</div>
  </div>
</section>''' % cells
CTA = link(fp.CTA).replace('class="kk" href="#"', 'class="kk" href="{{url content.kakaoUrl}}" rel="noopener" target="_blank"')
def phero(field, name, en, h1, sub, crumb=None):
    return '''<section class="phero">
  %s
  <div class="wrap">
    <div class="crumb"><a href="{{link "/"}}">홈</a><span>·</span><span>%s</span></div>
    <div class="en">%s</div>
    <h1>%s</h1>
    <p>%s</p>
  </div>
</section>''' % (slot(field, alt=name + ' 현장 사진', lazy=False), name, en, h1, sub)
def faq_static(items):
    d = ''.join('\n      <details%s><summary>%s</summary><div class="a">%s</div></details>' % (' open' if i == 0 else '', q, a) for i, (q, a) in enumerate(items))
    ld = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}, ensure_ascii=False)
    return '''<section class="faq">
  <div class="wrap">
    <div class="eyebrow reveal">FAQ</div>
    <h2 class="h2 reveal" data-delay="1">자주 묻는 질문</h2>
    <div class="list reveal" data-delay="2">%s
    </div>
  </div>
  <script type="application/ld+json">%s</script>
</section>''' % (d, ld)

# ── 페이지 ─────────────────────────────────────────────────────────────────
pages_out = {}
# 메인
sec = lambda name: re.search(r'<section class="%s"[^>]*>.*?</section>' % name, F, re.S).group(0)
trust = esc(sec('trust'))
trust = re.sub(r'<div class="stat-grid">.*?</div>\s*</div>\s*<div class="clients">', '''<div class="stat-grid">
        {{#each content.stats}}<div class="stat reveal"><b><span data-count="{{value}}">{{value}}</span>{{#if suffix}}<small>{{suffix}}</small>{{/if}}</b><span>{{label}}</span></div>{{/each}}
      </div>
    </div>
    <div class="clients">''', trust, flags=re.S)
trust = re.sub(r'<div class="marquee__track">.*?</div>', '<div class="marquee__track">{{#each content.clients}}{{#if logo}}<img class="client-logo" src="{{image logo}}" alt="{{name}}" loading="lazy">{{else}}<span>{{name}}</span>{{/if}}{{/each}}</div>', trust, flags=re.S)
svc = sec('svc-sec') if False else re.search(r'<section[^>]*>\s*<div class="wrap">\s*<div class="eyebrow reveal">Services</div>.*?</section>', F, re.S).group(0)
for f, k in KEY.items():
    svc = re.sub(r'href="%s"><img src="[^"]+" alt="" loading="lazy">' % re.escape(f), lambda m: 'href="{{link "/%s"}}">%s' % (k, slot(CARD[k], alt=FULL[k])), svc)
svc = link(esc(svc)).replace(' style="opacity:.95;display:block"', '')
wk = esc(sec('works'))
wk = re.sub(r'<div class="masonry" data-works>.*?</div>\s*<div class="more">', '''<div class="masonry" data-works>
      {{#each content.works}}<a class="work reveal" data-c="{{cat}}" role="button" tabindex="0" data-full="{{image image}}" data-lb><div class="ph"><img src="{{image image}}" alt="{{title}}" loading="lazy"></div><div class="cap">{{#if kicker}}<div class="k">{{kicker}}</div>{{/if}}<h3>{{title}}</h3>{{#if desc}}<p>{{desc}}</p>{{/if}}</div></a>{{/each}}
    </div>
    <div class="more">''', wk, flags=re.S)
strip_row = '{{#each content.strip}}<img src="{{image image}}" alt="{{alt image "소로롱 현장 사진"}}" loading="lazy">{{/each}}'
strip = '''<section class="strip" aria-label="현장 사진 모음">
  <div class="row" data-strip>%s</div>
  <div class="row rev" data-strip>%s</div>
</section>''' % (strip_row, strip_row)
tag = re.search(r'<div class="txt">(.*?)</div>\s*<div class="ctrl"', F, re.S).group(1).replace('assets/logo/mark-white.svg', '{{asset "img/mark-white.svg"}}').replace('event & balloon', 'event &amp; balloon')
hero_html = '''<section class="hero" id="top">
  {{#each content.heroSlides}}<div class="slide{{#if @first}} on{{/if}}"><img src="{{image image}}" alt="{{alt image "소로롱 풍선 연출 현장"}}"></div>{{else}}<div class="slide on"><img src="{{asset "img/hero.webp"}}" alt="소로롱 풍선 연출 현장"></div>{{/each}}
  <div class="wrap">
    <div class="txt">%s</div>
    <div class="ctrl" role="group" aria-label="메인 사진 선택" data-hero-dots></div>
  </div>
</section>''' % tag
faq_home = '''<section class="faq" id="faq">
  <div class="wrap">
    <div class="eyebrow reveal">FAQ</div>
    <h2 class="h2 reveal" data-delay="1">자주 묻는 질문</h2>
    <div class="list reveal" data-delay="2">{{#each content.faq}}<details{{#if @first}} open{{/if}}><summary>{{question}}</summary><div class="a">{{answer}}</div></details>{{/each}}</div>
  </div>
</section>'''
contact_home = '''<section class="contact" id="contact">
  <div class="wrap grid">
    <div>
      <div class="eyebrow reveal">Contact</div>
      <h2 class="h2 reveal" data-delay="1">상담 신청</h2>
      <p class="lead reveal" data-delay="2">행사 날짜와 장소, 원하는 분위기를 남겨주시면 어울리는 연출과 견적을 제안드립니다.</p>
      %s
    </div>
    %s
  </div>
</section>''' % (WAYS, FORM)
popup = '''{{#if content.popupOn}}{{#if content.popupImage}}<div class="popup" data-popup data-start="{{content.popupStart}}" data-end="{{content.popupEnd}}" hidden>
  <div class="popup__box" role="dialog" aria-label="이벤트 안내">
    {{#if content.popupLink}}<a href="{{url content.popupLink}}"><img src="{{image content.popupImage}}" alt="{{alt content.popupImage "이벤트 안내"}}"></a>{{else}}<img src="{{image content.popupImage}}" alt="{{alt content.popupImage "이벤트 안내"}}">{{/if}}
    <div class="popup__foot"><button type="button" data-popup-today>오늘 하루 보지 않기</button><button type="button" data-popup-close>닫기</button></div>
  </div>
</div>{{/if}}{{/if}}'''
rev_sec = re.search(r'<section class="reviews".*?</section>', F, re.S).group(0)
rev_sec = re.sub(r'<div class="ggrid rgrid reveal" data-delay="2">.*?</div>', '<div class="ggrid rgrid reveal" data-delay="2">{{#each content.galReview}}<a href="{{link "/review"}}"><img src="{{image image}}" alt="{{alt image "연예인 서포트 현장 사진"}}" loading="lazy"></a>{{/each}}</div>', rev_sec, flags=re.S)
rev_sec = rev_sec.replace('href="f-review.html"', 'href="{{link "/review"}}"')
all_cats = ['biz', 'sch', 'fam', 'wrt', 'flw', 'hel', 'rnt']
pages_out['index.html'] = page('\n\n'.join([hero_html, trust, link(svc), wk, strip, gallery('현장 사진 모음', '소로롱이 직접 꾸민 현장 사진을 분류별로 모았습니다. 사진을 누르면 크게 볼 수 있어요.', all_cats), rev_sec, faq_home, contact_home, popup]))

def intro(p, k):
    incl = ''.join('<li>%s</li>' % x for x in p['incl'])
    items = ''.join('\n      <div class="item reveal"%s><div class="ph">%s</div><div class="t"><div class="no">%02d</div><h3>%s</h3><p>%s</p></div></div>' % ('' if i == 0 else ' data-delay="%d"' % i, slot('%sItem%d' % (k, i + 1), alt=it[2]), i + 1, it[2], it[3]) for i, it in enumerate(p['items']))
    return '''<section class="intro">
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
</section>''' % (p['h2'], p['intro'], incl, items)
STEPS = fp.steps()
for p in PAGES:
    k = KEY[p['slug']]
    cats = [g for g, _ in GALLERIES[k]]
    pages_out[k + '.html'] = page('\n\n'.join([phero(k + 'Hero', p['name'], p['en'], p['h1'], p['sub']), intro(p, k), gallery(p['short'] + ' 현장 사진', '사진을 누르면 크게 볼 수 있어요.', cats), STEPS, faq_static(p['faq']), CTA, others(k)]))
# 상담문의
prep = [('행사 날짜 · 시간', '설치 가능한 시간과 행사 시작 시간을 함께 알려주세요.'), ('장소 · 공간 크기', '실내외 여부, 천장 높이, 설치할 벽이나 무대 크기를 알려주세요.'), ('인원 · 예산', '대략적인 참석 인원과 생각하는 예산이 있으면 맞춰 제안드려요.'), ('참고 사진', '원하는 분위기의 사진이나 로고, 브랜드 컬러를 보내주세요.')]
pl = ''.join('<li class="reveal"%s><b>%s</b><span>%s</span></li>' % ('' if i == 0 else ' data-delay="%d"' % i, a, b) for i, (a, b) in enumerate(prep))
pages_out['contact.html'] = page('\n\n'.join([
    phero('contactHero', '상담문의', 'Contact', '어떤 행사든 편하게 물어보세요', '행사 날짜와 장소, 원하는 분위기를 남겨주시면 어울리는 연출과 견적을 제안드립니다.'),
    '''<section class="prep-sec">
  <div class="wrap">
    <div class="eyebrow reveal">Before you ask</div>
    <h2 class="h2 reveal" data-delay="1">이 네 가지를 알려주시면 견적이 빨라요</h2>
    <ul class="prep">%s</ul>
  </div>
</section>''' % pl,
    '''<section class="contact" id="form">
  <div class="wrap grid">
    <div>
      <div class="eyebrow reveal">Contact</div>
      <h2 class="h2 reveal" data-delay="1">상담 신청</h2>
      <p class="lead reveal" data-delay="2">카카오톡이 가장 빨라요. 참고 사진도 함께 보내주시면 바로 확인합니다.</p>
      %s
    </div>
    %s
  </div>
</section>''' % (WAYS, FORM), STEPS, faq_static(FAQ_ALL[:4]), others('')]))
PRIVACY = '''<section class="policy">
  <div class="wrap">
    <h1>개인정보 처리방침</h1>
    <p>소로롱 이벤트&amp;벌룬은 상담 신청을 처리하기 위해 아래와 같이 개인정보를 수집 · 이용합니다.</p>
    <h2>수집 항목</h2>
    <p>이름, 연락처, 행사 종류, 행사 날짜, 장소, 문의 내용, 첨부한 참고 사진</p>
    <h2>이용 목적</h2>
    <p>행사 상담과 견적 안내, 일정 조율에만 사용합니다.</p>
    <h2>보유 기간</h2>
    <p>상담 완료 후 1년간 보관한 뒤 파기합니다. 법령에 따라 보관해야 하는 경우에는 해당 기간 동안 보관합니다.</p>
    <h2>동의를 거부할 권리</h2>
    <p>개인정보 수집 · 이용에 동의하지 않을 수 있으며, 이 경우 상담 접수는 카카오톡이나 전화로 받을 수 있습니다.</p>
    <h2>처리 위탁</h2>
    <p>사이트 운영과 접수 보관은 탱탱소프트에 위탁합니다.</p>
    <h2>개인정보 보호책임자</h2>
    <p>{{content.privacyOwner}}{{#if content.phone}} · <a href="tel:{{tel content.phone}}">{{content.phone}}</a>{{/if}}</p>
  </div>
</section>'''
pages_out['privacy.html'] = page(PRIVACY)

# ── site.json ──────────────────────────────────────────────────────────────
PAGE_META = [
    {'path': '/', 'file': 'index.html', 'title': '소로롱 이벤트&벌룬 | 기업 · 학교 행사 풍선 포토존과 공간 연출', 'description': '소로롱 이벤트&벌룬은 경기 광주를 기반으로 기업 시상식과 기념식, 관공서와 학교 행사, 돌잔치의 포토존과 풍선 공간 연출을 디자인부터 설치까지 직접 맡습니다.', 'menu': False},
]
DESC = {'biz': '소로롱은 기업 시상식과 기념식, 매장 오픈과 브랜드 팝업, 관공서 행사, 유치원과 학교 입학식 · 졸업식의 포토월과 풍선 장식을 설치와 철거까지 맡습니다.',
        'family': '소로롱은 돌잔치와 칠순, 생일과 프러포즈 같은 가족 행사의 포토존과 풍선 장식을 원하는 분위기에 맞춰 디자인하고 현장 설치까지 맡습니다.',
        'helium': '소로롱은 헬륨풍선과 로고 인쇄 풍선, 문구를 넣은 레터링 풍선을 행사 규모에 맞춰 제작하고 현장 세팅까지 맡습니다.',
        'flower': '소로롱은 자이언트플라워와 꽃풍선, 벌룬화환을 제작해 개업과 전시, 축하 행사의 공간을 화사하게 연출합니다.',
        'print': '소로롱은 폼보드와 포맥스, 실사 출력물을 제작해 포토월과 안내물, 캐릭터 조형을 풍선 장식과 함께 준비합니다.',
        'review': '소로롱이 연예인 생일과 촬영장 응원, 팬 서포트로 제작한 꽃풍선과 풍선 꽃다발, 커피차와 푸드트럭 장식 사진을 모았습니다. 단체 주문과 문구 제작도 상담할 수 있습니다.',
        'rental': '소로롱은 레드카펫과 천막, 트러스 포토존, 무대조명, 음향장비와 감독, 행사 인력 섭외까지 풍선 장식과 함께 행사 장비를 일괄 준비합니다.'}
for p in PAGES:
    k = KEY[p['slug']]
    PAGE_META.append({'path': '/' + k, 'file': k + '.html', 'title': '%s | 소로롱 이벤트&벌룬' % FULL[k], 'menuLabel': NAVL.get(k, FULL[k]), 'description': DESC[k]})
PAGE_META.append({'path': '/contact', 'file': 'contact.html', 'title': '상담문의 | 소로롱 이벤트&벌룬', 'menuLabel': '상담문의', 'description': '행사 날짜와 장소, 원하는 분위기를 남겨주시면 소로롱이 어울리는 풍선 연출과 견적을 제안드립니다. 카카오톡과 전화, 상담 접수 폼으로 문의할 수 있습니다.'})
PAGE_META.append({'path': '/privacy', 'file': 'privacy.html', 'title': '개인정보 처리방침 | 소로롱 이벤트&벌룬', 'menu': False, 'description': '소로롱 이벤트&벌룬이 상담 신청을 처리하며 수집하는 개인정보의 항목, 이용 목적, 보유 기간과 보호책임자를 안내합니다.'})
site = {
    'id': 'sororong', 'name': '소로롱 이벤트&벌룬', 'lang': 'ko', 'pages': PAGE_META,
    'content': {'schema': {'fields': fields, 'order': order}, 'defaults': defaults},
    'forms': [{'key': 'consult', 'title': '상담 신청', 'fields': [
        {'name': 'name', 'label': '이름', 'type': 'text', 'required': True, 'maxLength': 40},
        {'name': 'phone', 'label': '연락처', 'type': 'tel', 'required': True, 'maxLength': 20},
        {'name': 'kind', 'label': '행사 종류', 'type': 'select', 'options': ['기업 · 관공서 · 학교행사', '돌잔치 · 개인행사', '헬륨 · 인쇄 · 레터링풍선', '자이언트플라워 · 꽃풍선 · 벌룬화환', '폼보드 · 포맥스 · 실사물 제작', '행사장비 렌탈', '기타']},
        {'name': 'date', 'label': '행사 날짜', 'type': 'date'},
        {'name': 'place', 'label': '장소', 'type': 'text', 'maxLength': 120},
        {'name': 'message', 'label': '문의 내용', 'type': 'textarea', 'maxLength': 2000}],
        'consent': '상담 목적의 개인정보 수집 · 이용에 동의합니다.', 'attachments': {'max': 3, 'label': '참고 사진'}, 'success': '접수되었습니다. 남겨주신 연락처로 곧 연락드리겠습니다.'}],
    'admin': {'menus': {'submissions': '상담 문의', 'content': '사진 관리', 'collections': False}, 'content': {'sections': sections}},
    'seo': {'indexable': True, 'industry': 'general', 'organization': {'type': 'LocalBusiness', 'fields': {
        'name': '소로롱 이벤트&벌룬', 'alternateName': 'sororong', 'description': '기업 시상식과 기념식, 브랜드 팝업, 관공서와 학교 행사, 돌잔치의 포토존과 풍선 공간 연출을 맡는 경기 광주의 풍선 이벤트 업체입니다.', 'telephone': '{{content.phone}}', 'address': {'@type': 'PostalAddress', 'addressLocality': '광주시', 'addressRegion': '경기도', 'addressCountry': 'KR'}, 'areaServed': ['서울', '경기', '대한민국'], 'sameAs': ['{{content.instagramUrl}}', '{{content.kakaoUrl}}', '{{content.blogUrl}}']}},
        'summary': '소로롱 이벤트&벌룬은 경기 광주를 기반으로 기업 시상식과 기념식, 브랜드 팝업, 관공서와 학교 행사, 돌잔치의 포토존과 풍선 공간 연출을 디자인부터 설치와 철거까지 직접 맡는 풍선 이벤트 업체입니다.',
        'facts': ['본사: 경기도 광주시.', '서비스: 기업 · 관공서 · 학교행사, 돌잔치 · 개인행사, 헬륨 · 인쇄 · 레터링풍선, 자이언트플라워 · 꽃풍선 · 벌룬화환, 폼보드 · 포맥스 · 실사물, 행사장비 렌탈.', '서비스 지역: 서울 · 경기 중심, 전국 출장 설치 가능.'],
        'faq': {'content': 'faq', 'question': 'question', 'answer': 'answer', 'page': '/'}, 'favicon': 'img/mark-pink.svg', 'ogImage': 'img/og.png', 'indexMedia': True},
    'csp': {'styleSrc': ['https://cdn.jsdelivr.net', 'https://fonts.googleapis.com'], 'fontSrc': ['https://cdn.jsdelivr.net', 'https://fonts.gstatic.com']},
}

# ── 쓰기 ───────────────────────────────────────────────────────────────────
for d in (OUT, TPL):
    if os.path.exists(d): shutil.rmtree(d)
os.makedirs(OUT + '/pages'); os.makedirs(OUT + '/partials'); os.makedirs(TPL + '/css'); os.makedirs(TPL + '/js'); os.makedirs(TPL + '/img')
def w(path, text): io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
w(OUT + '/site.json', json.dumps(site, ensure_ascii=False, indent=2) + '\n')
for name, html in pages_out.items(): w(OUT + '/pages/' + name, html)
for name, html in (('head', HEAD), ('header', HEADER), ('footer', FOOTER), ('layout', LAYOUT)): w(OUT + '/partials/%s.html' % name, html + '\n')
css = ''.join(io.open(os.path.join(ROOT, 'assets', n), encoding='utf-8').read() + '\n' for n in ('common.css', 'f.css', 'f-sub.css'))
imports = re.findall(r"@import url\([^)]*\);\n", css)
css = ''.join(imports) + re.sub(r"@import url\([^)]*\);\n", '', css) + io.open(os.path.join(ROOT, 'tools/cms_extra.css'), encoding='utf-8').read()
w(TPL + '/css/site.css', css)
shutil.copy(os.path.join(ROOT, 'tools/cms_site.js'), TPL + '/js/site.js')
for n in ('logo-pink.png', 'mark-white.svg', 'mark-pink.svg'): shutil.copy(os.path.join(ROOT, 'assets/logo', n), TPL + '/img/' + n)
shutil.copy(os.path.join(ROOT, 'assets/og/og.png'), TPL + '/img/og.png')
def webp(src, dst, edge=1280, q=72):
    im = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, src))).convert('RGB'); im.thumbnail((edge, edge), Image.LANCZOS); im.save(dst, 'WEBP', quality=q, method=6)
for field, src in fallbacks.items(): webp(src, '%s/img/%s.webp' % (TPL, field))
webp(real(hero[0][0], hero[0][1]), TPL + '/img/hero.webp', 1600, 74)
w(os.path.join(ROOT, 'tools/cms_seed.json'), json.dumps(seed, ensure_ascii=False, indent=1))

n = sum(len(v) if isinstance(v, list) else 1 for v in seed.values())
files = set()
for v in seed.values():
    for x in (v if isinstance(v, list) else [v]): files.add(x['file'])
size = sum(os.path.getsize(os.path.join(TPL, 'img', f)) for f in os.listdir(TPL + '/img'))
print('pages', list(pages_out), 'sections', [s['key'] for s in sections])
print('seed 칸', n, '고유 사진', len(files), '기본 사진 용량 MB %.1f' % (size / 1e6))
